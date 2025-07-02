"""Test lazy loading of optional modules."""

import pytest


def test_core_import():
    """Test that core contextframe imports work without optional dependencies."""
    import contextframe

    assert contextframe.__version__
    assert hasattr(contextframe, 'FrameDataset')
    assert hasattr(contextframe, 'FrameRecord')


def test_builders_import():
    """Test that builders module can be imported."""
    from contextframe import builders

    assert hasattr(builders, 'extract')
    assert hasattr(builders, 'embed')
    assert hasattr(builders, 'enhance')
    assert hasattr(builders, 'encode')
    assert hasattr(builders, 'serve')


def test_extract_lazy_loading_error():
    """Test that extract module shows helpful error when dependencies missing."""
    from contextframe import builders

    with pytest.raises(ImportError) as exc_info:
        builders.extract.extract_pdf("test.pdf")

    assert "extract" in str(exc_info.value)
    assert "pip install" in str(exc_info.value)
    assert "contextframe[extract]" in str(exc_info.value)


def test_embed_lazy_loading_error():
    """Test that embed module shows helpful error when dependencies missing."""
    from contextframe import builders

    with pytest.raises(ImportError) as exc_info:
        builders.embed.generate_openai_embeddings("test")

    assert "embed" in str(exc_info.value)
    assert "pip install" in str(exc_info.value)
    assert "contextframe[embed]" in str(exc_info.value)


def test_enhance_lazy_loading_error():
    """Test that enhance module shows helpful error when dependencies missing."""
    from contextframe import builders

    with pytest.raises(ImportError) as exc_info:
        builders.enhance.enhance_with_openai("test")

    assert "enhance" in str(exc_info.value)
    assert "pip install" in str(exc_info.value)
    assert "contextframe[enhance]" in str(exc_info.value)


def test_encode_lazy_loading_error():
    """Test that encode module shows helpful error when dependencies missing."""
    from contextframe import builders

    with pytest.raises(ImportError) as exc_info:
        builders.encode.encode_to_mp4("test", "output")

    assert "encode" in str(exc_info.value)
    assert "pip install" in str(exc_info.value)
    assert "contextframe[encode]" in str(exc_info.value)


def test_serve_lazy_loading_error():
    """Test that serve module shows helpful error when dependencies missing."""
    from contextframe import builders

    with pytest.raises(ImportError) as exc_info:
        builders.serve.create_mcp_server("test")

    assert "serve" in str(exc_info.value)
    assert "pip install" in str(exc_info.value)
    assert "contextframe[serve]" in str(exc_info.value)
