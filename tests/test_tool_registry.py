"""
Tests for the dynamic tool registry.
"""

import unittest
import threading
import time
from unittest.mock import patch, MagicMock

from tools.registry import ToolRegistry, ToolMetadata, register_tool, get_registry


class TestToolRegistry(unittest.TestCase):
    """Test cases for the ToolRegistry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a fresh registry for each test
        self.registry = ToolRegistry()
        self.registry.clear()
    
    def test_singleton_pattern(self):
        """Test that ToolRegistry implements singleton pattern."""
        registry1 = ToolRegistry()
        registry2 = ToolRegistry()
        self.assertIs(registry1, registry2)
    
    def test_tool_registration(self):
        """Test basic tool registration."""
        def sample_tool(x: int, y: int) -> int:
            return x + y
        
        # Register tool
        result = self.registry.register("add", sample_tool, "Adds two numbers")
        self.assertTrue(result)
        
        # Check tool exists
        self.assertTrue(self.registry.has_tool("add"))
        self.assertEqual(self.registry.get_tool("add"), sample_tool)
        
        # Try to register again (should fail)
        result = self.registry.register("add", sample_tool, "Adds two numbers")
        self.assertFalse(result)
    
    def test_tool_unregistration(self):
        """Test tool unregistration."""
        def sample_tool():
            return "test"
        
        # Register and then unregister
        self.registry.register("test", sample_tool)
        self.assertTrue(self.registry.has_tool("test"))
        
        result = self.registry.unregister("test")
        self.assertTrue(result)
        self.assertFalse(self.registry.has_tool("test"))
        
        # Try to unregister non-existent tool
        result = self.registry.unregister("nonexistent")
        self.assertFalse(result)
    
    def test_tool_metadata(self):
        """Test tool metadata storage and retrieval."""
        def sample_tool(name: str = "World") -> str:
            """Says hello to someone."""
            return f"Hello, {name}!"
        
        self.registry.register(
            "hello",
            sample_tool,
            description="Greets someone",
            tags=["greeting", "social"],
            version="2.0.0"
        )
        
        metadata = self.registry.get_metadata("hello")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.name, "hello")
        self.assertEqual(metadata.description, "Greets someone")
        self.assertEqual(metadata.tags, ["greeting", "social"])
        self.assertEqual(metadata.version, "2.0.0")
    
    def test_list_operations(self):
        """Test listing tools and metadata."""
        def tool1():
            return 1
        
        def tool2():
            return 2
        
        self.registry.register("tool1", tool1, tags=["category1"])
        self.registry.register("tool2", tool2, tags=["category2"])
        
        # Test list_tools
        tools = self.registry.list_tools()
        self.assertEqual(set(tools), {"tool1", "tool2"})
        
        # Test list_metadata
        metadata_list = self.registry.list_metadata()
        self.assertEqual(len(metadata_list), 2)
        
        # Test list_tools_with_metadata
        tools_with_metadata = self.registry.list_tools_with_metadata()
        self.assertIn("tool1", tools_with_metadata)
        self.assertIn("tool2", tools_with_metadata)
        self.assertEqual(tools_with_metadata["tool1"]["name"], "tool1")
    
    def test_hot_swap(self):
        """Test hot-swapping tool implementations."""
        def original_tool():
            return "original"
        
        def new_tool():
            return "new"
        
        # Register original
        self.registry.register("swappable", original_tool)
        self.assertEqual(self.registry.get_tool("swappable")(), "original")
        
        # Hot swap
        result = self.registry.hot_swap("swappable", new_tool)
        self.assertTrue(result)
        self.assertEqual(self.registry.get_tool("swappable")(), "new")
        
        # Try to swap non-existent tool
        result = self.registry.hot_swap("nonexistent", new_tool)
        self.assertFalse(result)
    
    def test_get_tools_by_tag(self):
        """Test filtering tools by tag."""
        def tool1():
            return 1
        
        def tool2():
            return 2
        
        def tool3():
            return 3
        
        self.registry.register("tool1", tool1, tags=["math", "simple"])
        self.registry.register("tool2", tool2, tags=["math", "complex"])
        self.registry.register("tool3", tool3, tags=["text"])
        
        math_tools = self.registry.get_tools_by_tag("math")
        self.assertEqual(set(math_tools), {"tool1", "tool2"})
        
        simple_tools = self.registry.get_tools_by_tag("simple")
        self.assertEqual(simple_tools, ["tool1"])
        
        nonexistent_tools = self.registry.get_tools_by_tag("nonexistent")
        self.assertEqual(nonexistent_tools, [])
    
    def test_clear(self):
        """Test clearing all tools."""
        def tool():
            return "test"
        
        self.registry.register("test", tool)
        self.assertTrue(self.registry.has_tool("test"))
        
        self.registry.clear()
        self.assertFalse(self.registry.has_tool("test"))
        self.assertEqual(self.registry.list_tools(), [])
    
    def test_thread_safety(self):
        """Test thread safety of registry operations."""
        def worker_register(worker_id):
            for i in range(10):
                tool_name = f"tool_{worker_id}_{i}"
                def tool():
                    return f"result_{worker_id}_{i}"
                self.registry.register(tool_name, tool)
        
        def worker_unregister(worker_id):
            time.sleep(0.01)  # Let registration happen first
            for i in range(5):
                tool_name = f"tool_{worker_id}_{i}"
                self.registry.unregister(tool_name)
        
        # Start multiple threads
        threads = []
        for worker_id in range(3):
            t1 = threading.Thread(target=worker_register, args=(worker_id,))
            t2 = threading.Thread(target=worker_unregister, args=(worker_id,))
            threads.extend([t1, t2])
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have some tools remaining (not all were unregistered)
        remaining_tools = self.registry.list_tools()
        self.assertGreater(len(remaining_tools), 0)


class TestRegisterToolDecorator(unittest.TestCase):
    """Test cases for the @register_tool decorator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = get_registry()
        self.registry.clear()
    
    def test_basic_decoration(self):
        """Test basic tool decoration."""
        @register_tool()
        def test_function():
            """A test function."""
            return "test"
        
        self.assertTrue(self.registry.has_tool("test_function"))
        tool = self.registry.get_tool("test_function")
        self.assertEqual(tool(), "test")
    
    def test_custom_name_decoration(self):
        """Test decoration with custom name."""
        @register_tool(name="custom_name")
        def original_name():
            return "test"
        
        self.assertTrue(self.registry.has_tool("custom_name"))
        self.assertFalse(self.registry.has_tool("original_name"))
    
    def test_full_decoration(self):
        """Test decoration with all parameters."""
        @register_tool(
            name="full_tool",
            description="A fully decorated tool",
            tags=["test", "full"],
            version="3.0.0"
        )
        def complex_tool(x: int, y: str = "default") -> str:
            """Complex tool with parameters."""
            return f"{y}: {x}"
        
        metadata = self.registry.get_metadata("full_tool")
        self.assertEqual(metadata.name, "full_tool")
        self.assertEqual(metadata.description, "A fully decorated tool")
        self.assertEqual(metadata.tags, ["test", "full"])
        self.assertEqual(metadata.version, "3.0.0")
        
        # Test parameter extraction
        self.assertIn("x", metadata.parameters)
        self.assertIn("y", metadata.parameters)
    
    def test_docstring_extraction(self):
        """Test automatic description extraction from docstring."""
        @register_tool()
        def documented_function():
            """This is the first line of the docstring.
            
            This is additional documentation.
            """
            return "test"
        
        metadata = self.registry.get_metadata("documented_function")
        self.assertEqual(metadata.description, "This is the first line of the docstring.")


class TestToolMetadata(unittest.TestCase):
    """Test cases for the ToolMetadata class."""
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        def sample_tool():
            return "test"
        
        metadata = ToolMetadata(
            name="test",
            description="Test tool",
            parameters={"x": {"type": "int"}},
            tags=["test"],
            version="1.0.0",
            module="test_module",
            function=sample_tool
        )
        
        result = metadata.to_dict()
        expected = {
            "name": "test",
            "description": "Test tool",
            "parameters": {"x": {"type": "int"}},
            "tags": ["test"],
            "version": "1.0.0",
            "module": "test_module"
        }
        
        self.assertEqual(result, expected)
        # Function should not be in the dict
        self.assertNotIn("function", result)


if __name__ == "__main__":
    unittest.main()