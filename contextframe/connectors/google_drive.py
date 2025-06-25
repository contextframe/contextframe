"""Google Drive connector for importing documents into ContextFrame."""

import io
import mimetypes
from contextframe import FrameRecord
from contextframe.connectors.base import (
    AuthType,
    ConnectorConfig,
    SourceConnector,
    SyncResult,
)
from contextframe.schema import RecordType
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


class GoogleDriveConnector(SourceConnector):
    """Connector for importing Google Drive content."""

    GOOGLE_MIME_TYPES = {
        "application/vnd.google-apps.document": "text/plain",
        "application/vnd.google-apps.spreadsheet": "text/csv",
        "application/vnd.google-apps.presentation": "text/plain",
        "application/vnd.google-apps.drawing": "image/png",
    }

    EXPORT_FORMATS = {
        "application/vnd.google-apps.document": "text/plain",
        "application/vnd.google-apps.spreadsheet": "text/csv",
        "application/vnd.google-apps.presentation": "text/plain",
    }

    def __init__(self, config: ConnectorConfig, dataset):
        """Initialize Google Drive connector.

        Args:
            config: Connector configuration with Google Drive settings
            dataset: Target FrameDataset
        """
        super().__init__(config, dataset)

        # Configuration options
        self.folder_ids = config.sync_config.get("folder_ids", [])
        self.shared_drives = config.sync_config.get("shared_drives", [])
        self.file_patterns = config.sync_config.get("file_patterns", ["*"])
        self.exclude_patterns = config.sync_config.get("exclude_patterns", [])
        self.include_trashed = config.sync_config.get("include_trashed", False)
        self.export_google_formats = config.sync_config.get("export_google_formats", True)
        
        # Set up Google Drive API client
        self._setup_client()

    def _setup_client(self):
        """Set up Google Drive API client."""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaIoBaseDownload
            
            self.MediaIoBaseDownload = MediaIoBaseDownload
        except ImportError:
            raise ImportError(
                "google-api-python-client and google-auth are required. "
                "Install with: pip install google-api-python-client google-auth"
            )

        if self.config.auth_type == AuthType.OAUTH:
            # OAuth flow for user authentication
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow

            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
            
            creds = None
            token_data = self.config.auth_config.get("token_data")
            
            if token_data:
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_config(
                        self.config.auth_config.get("client_config"),
                        SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials back to config
                self.config.auth_config["token_data"] = {
                    "token": creds.token,
                    "refresh_token": creds.refresh_token,
                    "token_uri": creds.token_uri,
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "scopes": creds.scopes
                }
            
            self.service = build('drive', 'v3', credentials=creds)
            
        elif self.config.auth_type == AuthType.API_KEY:
            # Service account authentication
            credentials = service_account.Credentials.from_service_account_info(
                self.config.auth_config.get("service_account_info"),
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            self.service = build('drive', 'v3', credentials=credentials)
        else:
            raise ValueError("Google Drive requires OAuth or service account auth")

    def validate_connection(self) -> bool:
        """Validate Google Drive connection."""
        try:
            # Try to get user info or list files
            about = self.service.about().get(fields="user").execute()
            self.logger.info(f"Connected to Google Drive as: {about['user']['displayName']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to validate Google Drive connection: {e}")
            return False

    def discover_content(self) -> dict[str, Any]:
        """Discover Google Drive content structure."""
        discovery = {
            "drive_info": {},
            "folders": [],
            "file_stats": {
                "total_files": 0,
                "file_types": {},
                "total_size": 0,
            },
            "shared_drives": []
        }

        try:
            # Get drive info
            about = self.service.about().get(
                fields="user,storageQuota"
            ).execute()
            
            discovery["drive_info"] = {
                "user": about["user"]["displayName"],
                "email": about["user"]["emailAddress"],
                "storage_used": about.get("storageQuota", {}).get("usage", 0),
                "storage_limit": about.get("storageQuota", {}).get("limit", 0),
            }

            # Discover shared drives
            if self.shared_drives:
                shared_drives = self.service.drives().list(
                    pageSize=100,
                    fields="drives(id,name)"
                ).execute()
                
                discovery["shared_drives"] = [
                    {"id": d["id"], "name": d["name"]}
                    for d in shared_drives.get("drives", [])
                ]

            # Discover folders and files
            query_parts = []
            if not self.include_trashed:
                query_parts.append("trashed=false")
            
            # Add folder filters
            if self.folder_ids:
                folder_queries = [f"'{fid}' in parents" for fid in self.folder_ids]
                query_parts.append(f"({' or '.join(folder_queries)})")
            
            query = " and ".join(query_parts) if query_parts else None
            
            # Get files
            page_token = None
            while True:
                results = self.service.files().list(
                    q=query,
                    pageSize=1000,
                    fields="nextPageToken, files(id, name, mimeType, size, parents)",
                    pageToken=page_token
                ).execute()
                
                files = results.get('files', [])
                
                for file in files:
                    if file['mimeType'] == 'application/vnd.google-apps.folder':
                        discovery["folders"].append({
                            "id": file["id"],
                            "name": file["name"],
                            "parents": file.get("parents", [])
                        })
                    else:
                        discovery["file_stats"]["total_files"] += 1
                        size = int(file.get("size", 0))
                        discovery["file_stats"]["total_size"] += size
                        
                        # Track file types
                        mime_type = file["mimeType"]
                        discovery["file_stats"]["file_types"][mime_type] = \
                            discovery["file_stats"]["file_types"].get(mime_type, 0) + 1
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break

        except Exception as e:
            self.logger.error(f"Failed to discover Google Drive content: {e}")
            discovery["error"] = str(e)

        return discovery

    def sync(self, incremental: bool = True) -> SyncResult:
        """Sync Google Drive content to ContextFrame."""
        result = SyncResult(success=True)

        # Get last sync state if incremental
        last_sync_state = None
        if incremental:
            last_sync_state = self.get_last_sync_state()

        # Create main collection
        collection_id = self.create_collection(
            "Google Drive",
            "Documents and files from Google Drive"
        )

        # Track processed files
        processed_files: set[str] = set()

        # Process folders
        if self.folder_ids:
            for folder_id in self.folder_ids:
                self._sync_folder(
                    folder_id,
                    collection_id,
                    result,
                    last_sync_state,
                    processed_files
                )
        else:
            # Sync root folder
            self._sync_folder(
                "root",
                collection_id,
                result,
                last_sync_state,
                processed_files
            )

        # Process shared drives
        for drive_id in self.shared_drives:
            self._sync_shared_drive(
                drive_id,
                collection_id,
                result,
                last_sync_state,
                processed_files
            )

        # Save sync state
        if result.success:
            new_state = {
                "last_sync": datetime.now().isoformat(),
                "processed_files": list(processed_files),
            }
            self.save_sync_state(new_state)

        result.complete()
        return result

    def _sync_folder(
        self,
        folder_id: str,
        parent_collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        processed_files: set[str],
        folder_name: str = None
    ):
        """Sync a specific folder and its contents."""
        try:
            # Get folder info if not root
            if folder_id != "root" and not folder_name:
                folder = self.service.files().get(
                    fileId=folder_id,
                    fields="name"
                ).execute()
                folder_name = folder["name"]
            
            # Create collection for folder
            if folder_name:
                collection_id = self.create_collection(
                    f"Folder: {folder_name}",
                    f"Google Drive folder: {folder_name}"
                )
            else:
                collection_id = parent_collection_id

            # List files in folder
            query = f"'{folder_id}' in parents"
            if not self.include_trashed:
                query += " and trashed=false"

            page_token = None
            while True:
                results = self.service.files().list(
                    q=query,
                    pageSize=100,
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, webViewLink)",
                    pageToken=page_token
                ).execute()

                files = results.get('files', [])

                for file in files:
                    if file["mimeType"] == "application/vnd.google-apps.folder":
                        # Recursively sync subfolders
                        self._sync_folder(
                            file["id"],
                            collection_id,
                            result,
                            last_sync_state,
                            processed_files,
                            file["name"]
                        )
                    else:
                        # Check if file matches patterns
                        if self._matches_patterns(file["name"]):
                            # Check if needs update
                            if incremental and last_sync_state:
                                last_sync = datetime.fromisoformat(last_sync_state["last_sync"])
                                modified = datetime.fromisoformat(
                                    file["modifiedTime"].replace("Z", "+00:00")
                                )
                                if modified <= last_sync:
                                    continue

                            # Process file
                            frame = self.map_to_frame(file)
                            if frame:
                                frame.metadata["collection"] = collection_id
                                frame.metadata["collection_id"] = collection_id

                                try:
                                    # Check if exists
                                    existing = self.dataset.search(
                                        f"source_url:'{file['webViewLink']}'",
                                        limit=1
                                    )

                                    if existing:
                                        self.dataset.update(existing[0].metadata["uuid"], frame)
                                        result.frames_updated += 1
                                    else:
                                        self.dataset.add(frame)
                                        result.frames_created += 1

                                    processed_files.add(file["id"])

                                except Exception as e:
                                    result.frames_failed += 1
                                    result.add_error(f"Failed to import {file['name']}: {e}")

                page_token = results.get('nextPageToken')
                if not page_token:
                    break

        except Exception as e:
            result.add_error(f"Failed to sync folder {folder_id}: {e}")

    def _sync_shared_drive(
        self,
        drive_id: str,
        parent_collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        processed_files: set[str]
    ):
        """Sync a shared drive."""
        try:
            # Get drive info
            drive = self.service.drives().get(driveId=drive_id).execute()
            
            # Create collection for shared drive
            collection_id = self.create_collection(
                f"Shared Drive: {drive['name']}",
                f"Google Shared Drive: {drive['name']}"
            )

            # Sync drive contents (similar to folder sync but with supportsAllDrives=True)
            # Implementation would be similar to _sync_folder with drive-specific parameters

        except Exception as e:
            result.add_error(f"Failed to sync shared drive {drive_id}: {e}")

    def _matches_patterns(self, filename: str) -> bool:
        """Check if a filename matches the configured patterns."""
        from pathlib import Path
        
        path = Path(filename)
        
        # Check exclude patterns first
        for pattern in self.exclude_patterns:
            if path.match(pattern):
                return False
        
        # Check include patterns
        if not self.file_patterns or "*" in self.file_patterns:
            return True
            
        for pattern in self.file_patterns:
            if path.match(pattern):
                return True
                
        return False

    def map_to_frame(self, file_data: dict[str, Any]) -> FrameRecord | None:
        """Map Google Drive file to FrameRecord."""
        try:
            file_id = file_data["id"]
            mime_type = file_data["mimeType"]
            
            # Create base metadata
            metadata = {
                "title": file_data["name"],
                "record_type": RecordType.DOCUMENT,
                "source_type": "google_drive",
                "source_url": file_data.get("webViewLink", f"https://drive.google.com/file/d/{file_id}"),
                "source_file": file_data["name"],
                "updated_at": file_data.get("modifiedTime"),
                "custom_metadata": {
                    "x_google_drive_id": file_id,
                    "x_google_drive_mime_type": mime_type,
                    "x_google_drive_size": file_data.get("size", "0"),
                }
            }

            # Download file content
            text_content = None
            raw_data = None
            raw_data_type = None

            if mime_type in self.GOOGLE_MIME_TYPES and self.export_google_formats:
                # Export Google formats to readable format
                export_mime_type = self.EXPORT_FORMATS.get(mime_type, "text/plain")
                
                try:
                    response = self.service.files().export(
                        fileId=file_id,
                        mimeType=export_mime_type
                    ).execute()
                    
                    if isinstance(response, bytes):
                        text_content = response.decode('utf-8', errors='replace')
                    else:
                        text_content = str(response)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to export {file_data['name']}: {e}")
                    text_content = f"Google {mime_type} document: {file_data['name']}"
                    
            else:
                # Download regular files
                if mime_type.startswith("text/"):
                    try:
                        response = self.service.files().get_media(fileId=file_id).execute()
                        text_content = response.decode('utf-8', errors='replace')
                    except Exception as e:
                        self.logger.warning(f"Failed to download {file_data['name']}: {e}")
                        text_content = f"File: {file_data['name']}"
                elif mime_type.startswith("image/"):
                    # For images, store reference
                    raw_data_type = mime_type
                    text_content = f"Image file: {file_data['name']}"
                    # Could download image data here if needed
                else:
                    # Other binary files
                    text_content = f"Binary file: {file_data['name']} ({mime_type})"

            # Create frame
            return FrameRecord(
                text_content=text_content,
                metadata=metadata,
                raw_data=raw_data,
                raw_data_type=raw_data_type,
            )

        except Exception as e:
            self.logger.error(f"Failed to map file {file_data.get('name', 'Unknown')}: {e}")
            return None