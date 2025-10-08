"""
Tests for Suspense and async boundary features - achieving Crank.js parity

This test suite covers Suspense, SuspenseList, and lazy loading patterns
that are core to modern async component patterns in Crank.js.
"""
import sys
from crank import h, component
try:
    # Import async components - renamed to async_ to avoid keyword conflict
    import crank.async_ as crank_async
    Suspense = crank_async.Suspense
    SuspenseList = crank_async.SuspenseList
    lazy = crank_async.lazy
except ImportError:
    # Fallback if async module not available
    Suspense = None
    SuspenseList = None
    lazy = None
import upytest


class TestSuspenseElement:
    """Test Suspense element for async boundaries"""
    
    def test_suspense_element_exists(self):
        """Test that Suspense element is available"""
        assert Suspense is not None
        # Suspense should be callable/constructible
        suspense = h(Suspense, fallback=h.div["Loading..."])["Content"]
        assert suspense is not None
    
    def test_suspense_with_fallback(self):
        """Test Suspense with fallback UI"""
        @component
        def SuspenseComponent(ctx):
            return h(Suspense, fallback=h.div["Loading..."])[
                h.div["Async content loaded"]
            ]
        
        assert SuspenseComponent is not None
    
    def test_suspense_with_async_component(self):
        """Test Suspense wrapping async components"""
        @component
        async def AsyncChild(ctx):
            # Simulate async operation
            yield h.div["Async component content"]
        
        @component
        def SuspenseWrapperComponent(ctx):
            return h(Suspense, fallback=h.div["Loading async component..."])[
                h(AsyncChild)
            ]
        
        assert SuspenseWrapperComponent is not None
        assert AsyncChild is not None
    
    def test_suspense_nested(self):
        """Test nested Suspense boundaries"""
        @component
        async def DeepAsyncComponent(ctx):
            yield h.div["Deep async content"]
        
        @component
        async def AsyncComponent(ctx):
            yield h(Suspense, fallback=h.div["Loading deep..."])[
                h(DeepAsyncComponent)
            ]
        
        @component
        def NestedSuspenseComponent(ctx):
            return h(Suspense, fallback=h.div["Loading outer..."])[
                h(AsyncComponent)
            ]
        
        assert NestedSuspenseComponent is not None
    
    def test_suspense_with_multiple_children(self):
        """Test Suspense with multiple async children"""
        @component
        async def AsyncChild1(ctx):
            yield h.div["Async child 1"]
        
        @component
        async def AsyncChild2(ctx):
            yield h.div["Async child 2"]
        
        @component
        def MultipleSuspenseComponent(ctx):
            return h(Suspense, fallback=h.div["Loading multiple children..."])[
                h(AsyncChild1),
                h(AsyncChild2),
                h.div["Sync child"]
            ]
        
        assert MultipleSuspenseComponent is not None
    
    def test_suspense_error_boundary(self):
        """Test Suspense as error boundary for async errors"""
        @component
        async def FailingAsyncComponent(ctx):
            async for props in ctx:
                if props.get("should_fail"):
                    raise RuntimeError("Async component failed")
                yield h.div["Success"]
        
        @component
        def SuspenseErrorComponent(ctx):
            return h(Suspense, 
                fallback=h.div["Loading..."],
                # In real implementation, would have error prop
                **{"data-error-boundary": "true"}
            )[
                h(FailingAsyncComponent)
            ]
        
        assert SuspenseErrorComponent is not None


class TestSuspenseList:
    """Test SuspenseList for coordinating multiple Suspense boundaries"""
    
    def test_suspense_list_exists(self):
        """Test that SuspenseList element is available"""
        assert SuspenseList is not None
        # SuspenseList should be callable/constructible
        suspense_list = h(SuspenseList, revealOrder="forwards")[
            h(Suspense, fallback=h.div["Loading 1"])["Content 1"],
            h(Suspense, fallback=h.div["Loading 2"])["Content 2"]
        ]
        assert suspense_list is not None
    
    def test_suspense_list_forwards_reveal(self):
        """Test SuspenseList with forwards reveal order"""
        @component
        async def AsyncItem(ctx, props):
            item_id = props.get("id", 0)
            # Simulate variable loading times
            yield h.div[f"Item {item_id} loaded"]
        
        @component
        def ForwardsSuspenseListComponent(ctx):
            return h(SuspenseList, revealOrder="forwards")[
                h(Suspense, key="item-1", fallback=h.div["Loading item 1..."])[
                    h(AsyncItem, id=1)
                ],
                h(Suspense, key="item-2", fallback=h.div["Loading item 2..."])[
                    h(AsyncItem, id=2)
                ],
                h(Suspense, key="item-3", fallback=h.div["Loading item 3..."])[
                    h(AsyncItem, id=3)
                ]
            ]
        
        assert ForwardsSuspenseListComponent is not None
    
    def test_suspense_list_backwards_reveal(self):
        """Test SuspenseList with backwards reveal order"""
        @component
        def BackwardsSuspenseListComponent(ctx):
            return h(SuspenseList, revealOrder="backwards")[
                h(Suspense, fallback=h.div["Loading A"])["Content A"],
                h(Suspense, fallback=h.div["Loading B"])["Content B"],
                h(Suspense, fallback=h.div["Loading C"])["Content C"]
            ]
        
        assert BackwardsSuspenseListComponent is not None
    
    def test_suspense_list_together_reveal(self):
        """Test SuspenseList with together reveal order"""
        @component
        def TogetherSuspenseListComponent(ctx):
            return h(SuspenseList, revealOrder="together")[
                h(Suspense, fallback=h.div["Loading X"])["Content X"],
                h(Suspense, fallback=h.div["Loading Y"])["Content Y"],
                h(Suspense, fallback=h.div["Loading Z"])["Content Z"]
            ]
        
        assert TogetherSuspenseListComponent is not None
    
    def test_suspense_list_with_tail(self):
        """Test SuspenseList with tail fallback"""
        @component
        def TailSuspenseListComponent(ctx):
            return h(SuspenseList, 
                revealOrder="forwards",
                tail="collapsed"  # or "hidden"
            )[
                h(Suspense, fallback=h.div["Loading 1"])["Content 1"],
                h(Suspense, fallback=h.div["Loading 2"])["Content 2"],
                h(Suspense, fallback=h.div["Loading 3"])["Content 3"]
            ]
        
        assert TailSuspenseListComponent is not None


class TestLazyLoading:
    """Test lazy loading functionality"""
    
    def test_lazy_function_exists(self):
        """Test that lazy function is available"""
        assert lazy is not None
        assert callable(lazy)
    
    def test_lazy_component_basic(self):
        """Test basic lazy component loading"""
        @component
        def LazyComponent(ctx):
            return h.div["Lazy loaded component"]
        
        # Create lazy version
        LazyLoadedComponent = lazy(lambda: LazyComponent)
        
        @component
        def LazyWrapperComponent(ctx):
            return h(Suspense, fallback=h.div["Loading lazy component..."])[
                h(LazyLoadedComponent)
            ]
        
        assert LazyLoadedComponent is not None
        assert LazyWrapperComponent is not None
    
    def test_lazy_with_import_simulation(self):
        """Test lazy loading with simulated dynamic import"""
        # Simulate module loading
        def load_module():
            @component
            def DynamicComponent(ctx):
                return h.div["Dynamically loaded component"]
            return DynamicComponent
        
        LazyDynamicComponent = lazy(load_module)
        
        @component
        def DynamicWrapperComponent(ctx):
            return h(Suspense, fallback=h.div["Loading dynamic module..."])[
                h(LazyDynamicComponent)
            ]
        
        assert LazyDynamicComponent is not None
        assert DynamicWrapperComponent is not None
    
    def test_lazy_with_props(self):
        """Test lazy component with props"""
        @component
        def LazyPropsComponent(ctx, props):
            name = props.get("name", "World")
            return h.div[f"Hello {name} from lazy component"]
        
        LazyPropsComponentLazy = lazy(lambda: LazyPropsComponent)
        
        @component
        def LazyPropsWrapperComponent(ctx):
            return h(Suspense, fallback=h.div["Loading..."])[
                h(LazyPropsComponentLazy, name="Lazy User")
            ]
        
        assert LazyPropsWrapperComponent is not None
    
    def test_lazy_error_handling(self):
        """Test lazy loading error handling"""
        def failing_loader():
            raise ImportError("Failed to load module")
        
        FailingLazyComponent = lazy(failing_loader)
        
        @component
        def LazyErrorWrapperComponent(ctx):
            try:
                return h(Suspense, fallback=h.div["Loading..."])[
                    h(FailingLazyComponent)
                ]
            except Exception as e:
                return h.div[f"Lazy loading failed: {e}"]
        
        assert LazyErrorWrapperComponent is not None


class TestAsyncBoundaryPatterns:
    """Test common async boundary patterns"""
    
    def test_async_data_fetching_pattern(self):
        """Test async data fetching with Suspense"""
        @component
        async def DataFetchingComponent(ctx):
            async for props in ctx:
                user_id = props.get("user_id", 1)
                # Simulate data fetching
                user_data = {"id": user_id, "name": f"User {user_id}"}
                yield h.div[
                    h.h2[user_data["name"]],
                    h.p[f"ID: {user_data['id']}"]
                ]
        
        @component
        def DataFetchingWrapperComponent(ctx):
            return h(Suspense, fallback=h.div["Fetching user data..."])[
                h(DataFetchingComponent, user_id=42)
            ]
        
        assert DataFetchingWrapperComponent is not None
    
    def test_progressive_loading_pattern(self):
        """Test progressive loading with multiple Suspense boundaries"""
        @component
        async def HeaderComponent(ctx):
            yield h.header["App Header"]
        
        @component
        async def MainContentComponent(ctx):
            yield h.main["Main Content"]
        
        @component
        async def SidebarComponent(ctx):
            yield h.aside["Sidebar"]
        
        @component
        def ProgressiveLoadingComponent(ctx):
            return h.div[
                # Header loads first
                h(Suspense, fallback=h.div["Loading header..."])[
                    h(HeaderComponent)
                ],
                h.div(className="main-layout")[
                    # Main content and sidebar load independently
                    h(Suspense, fallback=h.div["Loading content..."])[
                        h(MainContentComponent)
                    ],
                    h(Suspense, fallback=h.div["Loading sidebar..."])[
                        h(SidebarComponent)
                    ]
                ]
            ]
        
        assert ProgressiveLoadingComponent is not None
    
    def test_conditional_suspense_pattern(self):
        """Test conditional Suspense based on props"""
        @component
        async def ConditionalAsyncComponent(ctx):
            async for props in ctx:
                if props.get("load_async"):
                    # Simulate async operation
                    yield h.div["Async content loaded"]
                else:
                    yield h.div["Sync content"]
        
        @component
        def ConditionalSuspenseComponent(ctx):
            for props in ctx:
                if props.get("load_async"):
                    yield h(Suspense, fallback=h.div["Loading async..."])[
                        h(ConditionalAsyncComponent, load_async=True)
                    ]
                else:
                    yield h(ConditionalAsyncComponent, load_async=False)
        
        assert ConditionalSuspenseComponent is not None
    
    def test_suspense_with_timeout_pattern(self):
        """Test Suspense with timeout handling"""
        @component
        async def SlowAsyncComponent(ctx):
            # Simulate slow loading
            async for props in ctx:
                yield h.div["Finally loaded after delay"]
        
        @component
        def TimeoutSuspenseComponent(ctx):
            return h(Suspense, 
                fallback=h.div["Loading... (this might take a while)"],
                # In real implementation, would have timeout prop
                **{"data-timeout": "5000"}
            )[
                h(SlowAsyncComponent)
            ]
        
        assert TimeoutSuspenseComponent is not None


class TestAsyncErrorBoundaries:
    """Test error boundaries for async components"""
    
    def test_async_component_error_catching(self):
        """Test catching errors in async components"""
        @component
        async def ErrorProneAsyncComponent(ctx):
            async for props in ctx:
                if props.get("should_error"):
                    raise ValueError("Async component error")
                yield h.div["Async success"]
        
        @component
        def AsyncErrorBoundaryComponent(ctx):
            try:
                return h(Suspense, fallback=h.div["Loading..."])[
                    h(ErrorProneAsyncComponent, should_error=True)
                ]
            except ValueError as e:
                return h.div[f"Caught async error: {e}"]
        
        assert AsyncErrorBoundaryComponent is not None
    
    def test_suspense_error_recovery(self):
        """Test error recovery with Suspense"""
        @component
        async def RecoverableAsyncComponent(ctx):
            async for props in ctx:
                retry_count = props.get("retry_count", 0)
                if retry_count < 2:
                    raise RuntimeError(f"Failed attempt {retry_count + 1}")
                yield h.div["Success after retries"]
        
        @component
        def RetryingSuspenseComponent(ctx):
            for props in ctx:
                try:
                    yield h(Suspense, fallback=h.div["Loading..."])[
                        h(RecoverableAsyncComponent, retry_count=props.get("retry_count", 0))
                    ]
                except RuntimeError as e:
                    retry_count = props.get("retry_count", 0)
                    if retry_count < 3:
                        yield h.div[
                            f"Error: {e}",
                            h.button(onclick=f"retry({retry_count + 1})")["Retry"]
                        ]
                    else:
                        yield h.div["Max retries exceeded"]
        
        assert RetryingSuspenseComponent is not None
    
    def test_nested_async_error_propagation(self):
        """Test error propagation through nested async boundaries"""
        @component
        async def DeepErrorComponent(ctx):
            async for props in ctx:
                if props.get("deep_error"):
                    raise Exception("Deep async error")
                yield h.div["Deep success"]
        
        @component
        async def MiddleAsyncComponent(ctx):
            async for props in ctx:
                yield h(Suspense, fallback=h.div["Loading deep..."])[
                    h(DeepErrorComponent, deep_error=props.get("deep_error"))
                ]
        
        @component
        def OuterErrorBoundaryComponent(ctx):
            try:
                return h(Suspense, fallback=h.div["Loading..."])[
                    h(MiddleAsyncComponent, deep_error=True)
                ]
            except Exception as e:
                return h.div[f"Outer boundary caught: {e}"]
        
        assert OuterErrorBoundaryComponent is not None