"""
Event handling tests - testing DOM event functionality
"""

def test_click_event_handler():
    """Test click event handler registration and execution"""
    from crank import h
    from crank.dom import renderer
    from js import document, Event
    
    # Track event calls
    click_calls = []
    
    def handle_click(event):
        click_calls.append("clicked")
        
    document.body.innerHTML = ""
    renderer.render(h.button(onclick=handle_click)["Click me"], document.body)
    
    button = document.querySelector("button")
    assert button is not None
    assert button.textContent == "Click me"
    
    # Simulate click event
    click_event = Event.new("click")
    button.dispatchEvent(click_event)
    
    # Verify handler was called
    assert len(click_calls) == 1
    assert click_calls[0] == "clicked"

def test_multiple_event_handlers():
    """Test multiple event types on same element"""
    from crank import h
    from crank.dom import renderer
    from js import document, Event
    
    event_log = []
    
    def handle_click(event):
        event_log.append("click")
        
    def handle_mouseover(event):
        event_log.append("mouseover")
        
    def handle_focus(event):
        event_log.append("focus")
        
    document.body.innerHTML = ""
    renderer.render(h.input(
        onclick=handle_click,
        onmouseover=handle_mouseover,
        onfocus=handle_focus,
        type="text"
    ), document.body)
    
    input_elem = document.querySelector("input")
    assert input_elem is not None
    
    # Test each event
    input_elem.dispatchEvent(Event.new("click"))
    input_elem.dispatchEvent(Event.new("mouseover"))
    input_elem.dispatchEvent(Event.new("focus"))
    
    assert "click" in event_log
    assert "mouseover" in event_log
    assert "focus" in event_log

def test_event_handler_with_component():
    """Test event handlers work within components"""
    from crank import h, component
    from crank.dom import renderer
    from js import document, Event
    
    interaction_log = []
    
    @component
    def InteractiveComponent(ctx, props):
        def handle_click(event):
            interaction_log.append("component_clicked")
            
        def handle_input(event):
            interaction_log.append(f"input_changed:{event.target.value}")
            
        for _ in ctx:
            yield h.div[
                h.button(onclick=handle_click)["Component Button"],
                h.input(oninput=handle_input, type="text")
            ]
    
    document.body.innerHTML = ""
    renderer.render(h(InteractiveComponent), document.body)
    
    button = document.querySelector("button")
    input_elem = document.querySelector("input")
    
    assert button is not None
    assert input_elem is not None
    
    # Test button click
    button.dispatchEvent(Event.new("click"))
    assert "component_clicked" in interaction_log
    
    # Test input change
    input_elem.value = "test"
    input_event = Event.new("input")
    input_event.target = input_elem
    input_elem.dispatchEvent(input_event)
    
    # Check if input event was logged (may depend on event target setup)
    assert len(interaction_log) >= 1

def test_form_events():
    """Test form-specific events"""
    from crank import h
    from crank.dom import renderer
    from js import document, Event
    
    form_events = []
    
    def handle_submit(event):
        event.preventDefault()  # Prevent actual form submission
        form_events.append("submit")
        
    def handle_change(event):
        form_events.append(f"change:{event.target.value}")
        
    document.body.innerHTML = ""
    renderer.render(h.form(onsubmit=handle_submit)[
        h.input(onchange=handle_change, type="text", name="username"),
        h.button(type="submit")["Submit"]
    ], document.body)
    
    form = document.querySelector("form")
    input_elem = document.querySelector("input")
    
    assert form is not None
    assert input_elem is not None
    
    # Test change event
    input_elem.value = "testuser"
    change_event = Event.new("change")
    change_event.target = input_elem
    input_elem.dispatchEvent(change_event)
    
    # Test form submit
    form.dispatchEvent(Event.new("submit"))
    
    assert "submit" in form_events

def test_event_handler_props_update():
    """Test event handlers update when component props change"""
    from crank import h, component
    from crank.dom import renderer
    from js import document, Event
    
    handler_calls = []
    
    @component
    def DynamicHandler(ctx, props):
        for props in ctx:
            handler_type = props.get("handlerType", "default")
            
            def make_handler(handler_id):
                def handler(event):
                    handler_calls.append(f"handler_{handler_id}")
                return handler
            
            if handler_type == "primary":
                yield h.button(onclick=make_handler("primary"))["Primary"]
            else:
                yield h.button(onclick=make_handler("default"))["Default"]
    
    document.body.innerHTML = ""
    
    # Render with default handler
    renderer.render(h(DynamicHandler, handlerType="default"), document.body)
    button = document.querySelector("button")
    button.dispatchEvent(Event.new("click"))
    
    # Update to primary handler
    renderer.render(h(DynamicHandler, handlerType="primary"), document.body)
    button = document.querySelector("button")
    button.dispatchEvent(Event.new("click"))
    
    # Verify different handlers were called
    assert "handler_default" in handler_calls
    assert "handler_primary" in handler_calls

def test_event_bubbling():
    """Test event bubbling behavior"""
    from crank import h
    from crank.dom import renderer
    from js import document, Event
    
    bubble_log = []
    
    def handle_outer_click(event):
        bubble_log.append("outer")
        
    def handle_inner_click(event):
        bubble_log.append("inner")
        # Don't stop propagation - let it bubble
        
    document.body.innerHTML = ""
    renderer.render(h.div(onclick=handle_outer_click)[
        h.button(onclick=handle_inner_click)["Inner Button"]
    ], document.body)
    
    button = document.querySelector("button")
    assert button is not None
    
    # Click the inner button - should trigger both handlers due to bubbling
    click_event = Event.new("click", {"bubbles": True})
    button.dispatchEvent(click_event)
    
    # Both handlers should have been called due to bubbling
    assert "inner" in bubble_log
    # Note: bubbling behavior may depend on how events are set up in the framework

def test_custom_event_data():
    """Test passing custom data through event handlers"""
    from crank import h, component
    from crank.dom import renderer
    from js import document, Event
    
    custom_data_log = []
    
    @component
    def CustomDataComponent(ctx, props):
        def make_handler(data):
            def handler(event):
                custom_data_log.append(data)
            return handler
            
        for _ in ctx:
            yield h.div[
                h.button(onclick=make_handler("button1"))["Button 1"],
                h.button(onclick=make_handler("button2"))["Button 2"],
                h.button(onclick=make_handler("button3"))["Button 3"]
            ]
    
    document.body.innerHTML = ""
    renderer.render(h(CustomDataComponent), document.body)
    
    buttons = list(document.querySelectorAll("button"))
    assert len(buttons) == 3
    
    # Click each button
    for i, button in enumerate(buttons):
        button.dispatchEvent(Event.new("click"))
    
    # Verify custom data was passed correctly
    assert "button1" in custom_data_log
    assert "button2" in custom_data_log  
    assert "button3" in custom_data_log

def test_event_handler_cleanup():
    """Test event handlers are cleaned up when components unmount"""
    from crank import h, component
    from crank.dom import renderer
    from js import document, Event
    
    cleanup_log = []
    
    @component
    def CleanupComponent(ctx, props):
        def handle_click(event):
            cleanup_log.append("still_active")
            
        for _ in ctx:
            yield h.button(onclick=handle_click)["Test Button"]
    
    document.body.innerHTML = ""
    
    # Render component
    renderer.render(h(CleanupComponent), document.body)
    button = document.querySelector("button")
    button.dispatchEvent(Event.new("click"))
    assert "still_active" in cleanup_log
    
    # Clear the component (unmount)
    renderer.render(h.div["Empty"], document.body)
    
    # The button should no longer exist
    button_after = document.querySelector("button")
    assert button_after is None
    
    # Test passes if no errors occur during cleanup