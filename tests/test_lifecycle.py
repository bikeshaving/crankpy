"""
Component lifecycle tests - schedule, after, cleanup, refresh
"""

def test_context_schedule():
    """Test ctx.schedule functionality"""
    from crank import h, component
    
    @component
    def ScheduleComponent(ctx):
        def scheduled_task():
            pass  # Scheduled task
        
        for _ in ctx:
            ctx.schedule(scheduled_task)
            yield h.div["Scheduled"]
    
    element = h(ScheduleComponent)
    assert element is not None

def test_context_after():
    """Test ctx.after functionality"""
    from crank import h, component
    
    @component
    def AfterComponent(ctx):
        def after_task():
            pass  # After render task
        
        for _ in ctx:
            ctx.after(after_task)
            yield h.div["After"]
    
    element = h(AfterComponent)
    assert element is not None

def test_context_cleanup():
    """Test ctx.cleanup functionality"""
    from crank import h, component
    
    @component
    def CleanupComponent(ctx):
        def cleanup_task():
            pass  # Cleanup task
        
        for _ in ctx:
            ctx.cleanup(cleanup_task)
            yield h.div["Cleanup"]
    
    element = h(CleanupComponent)
    assert element is not None

def test_context_refresh_decorator():
    """Test ctx.refresh as decorator"""
    from crank import h, component
    
    @component
    def RefreshComponent(ctx):
        @ctx.refresh
        def update_state():
            pass  # State update that triggers refresh
        
        for _ in ctx:
            yield h.div["Refresh"]
    
    element = h(RefreshComponent)
    assert element is not None

def test_context_refresh_method():
    """Test ctx.refresh as method call"""
    from crank import h, component
    
    @component
    def RefreshMethodComponent(ctx):
        for _ in ctx:
            ctx.refresh()  # Direct refresh call
            yield h.div["Refresh method"]
    
    element = h(RefreshMethodComponent)
    assert element is not None

def test_multiple_lifecycle_hooks():
    """Test component with multiple lifecycle hooks"""
    from crank import h, component
    
    @component
    def MultiLifecycleComponent(ctx):
        def scheduled():
            pass
        
        def after_render():
            pass
        
        def cleanup():
            pass
        
        for _ in ctx:
            ctx.schedule(scheduled)
            ctx.after(after_render)
            ctx.cleanup(cleanup)
            yield h.div["Multi lifecycle"]
    
    element = h(MultiLifecycleComponent)
    assert element is not None

def test_async_lifecycle_hooks():
    """Test async component with lifecycle hooks"""
    from crank import h, component
    
    @component
    async def AsyncLifecycleComponent(ctx):
        def cleanup_task():
            pass
        
        async for _ in ctx:
            ctx.cleanup(cleanup_task)
            yield h.div["Async lifecycle"]
    
    element = h(AsyncLifecycleComponent)
    assert element is not None

def test_context_props_access():
    """Test accessing props through context"""
    from crank import h, component
    
    @component
    def PropsAccessComponent(ctx):
        for _ in ctx:
            # Test props access
            props = ctx.props
            title = props.get("title", "default")
            yield h.div[f"Title: {title}"]
    
    element = h(PropsAccessComponent, title="Test")
    assert element is not None

def test_context_iteration():
    """Test context iteration patterns"""
    from crank import h, component
    
    @component
    def IterationComponent(ctx):
        count = 0
        for props in ctx:
            count += 1
            name = props.get("name", f"iteration-{count}")
            yield h.div[f"Iteration {count}: {name}"]
    
    element = h(IterationComponent, name="test")
    assert element is not None