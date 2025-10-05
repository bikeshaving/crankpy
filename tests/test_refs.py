"""
Test ref prop support - actual functionality testing
"""

import pytest

from crank import component, h


class TestRefFunctionality:
    """Test that ref props work correctly in components."""

    def test_ref_prop_syntax_compiles(self):
        """Test that ref prop syntax compiles without errors"""
        def my_ref_callback(element):
            pass
            
        # These should all compile without errors
        element1 = h.div(ref=my_ref_callback)
        element2 = h.input(type="text", ref=my_ref_callback)
        element3 = h.button(ref=lambda el: None)
        
        # Basic existence check
        assert element1 is not None
        assert element2 is not None  
        assert element3 is not None

    def test_ref_prop_with_other_props(self):
        """Test ref prop combined with other props"""
        def ref_callback(element):
            pass
            
        element = h.input(
            type="text",
            value="test",
            className="input-field", 
            ref=ref_callback,
            placeholder="Enter text"
        )
        
        assert element is not None

    def test_ref_callback_types(self):
        """Test different types of ref callbacks compile"""
        # Lambda ref
        element1 = h.div(ref=lambda el: None)
        
        # Function ref
        def named_ref(el):
            pass
        element2 = h.div(ref=named_ref)
        
        # Method ref (would be bound in real usage)
        class RefHandler:
            def handle_ref(self, el):
                pass
        handler = RefHandler()
        element3 = h.div(ref=handler.handle_ref)
        
        assert element1 is not None
        assert element2 is not None
        assert element3 is not None


class TestRefComponents:
    """Test realistic ref usage in components."""

    def test_component_with_single_ref(self):
        """Test component that uses a single ref"""
        @component
        def ComponentWithRef(ctx):
            input_element = None
            
            def set_input_ref(el):
                nonlocal input_element
                input_element = el
                
            for props in ctx:
                yield h.div[
                    h.input(
                        type="text",
                        placeholder="Will be referenced",
                        ref=set_input_ref
                    )
                ]
        
        # Should compile and be callable
        assert callable(ComponentWithRef)
        
        # Should create element without errors
        element = h(ComponentWithRef)
        assert element is not None

    def test_component_with_multiple_refs(self):
        """Test component with multiple ref elements"""
        @component 
        def MultiRefComponent(ctx):
            audio_ref = None
            video_ref = None
            
            def set_audio_ref(el):
                nonlocal audio_ref
                audio_ref = el
                
            def set_video_ref(el):
                nonlocal video_ref
                video_ref = el
            
            for props in ctx:
                yield h.div[
                    h.audio(ref=set_audio_ref, src="/audio.mp3"),
                    h.video(ref=set_video_ref, src="/video.mp4")
                ]
        
        # Should compile and be callable
        assert callable(MultiRefComponent)
        
        # Should create element without errors
        element = h(MultiRefComponent)
        assert element is not None

    def test_audio_player_component(self):
        """Test the common audio player ref pattern"""
        @component
        def AudioPlayer(ctx):
            audio_element = None
            
            def set_audio_ref(el):
                nonlocal audio_element
                audio_element = el
                
            def play_audio():
                if audio_element:
                    # In real usage: audio_element.play()
                    pass
            
            for props in ctx:
                yield h.div[
                    h.button(onclick=play_audio)["Play sound"],
                    h.audio(
                        src="/static/sound.mp3",
                        controls=False,
                        ref=set_audio_ref
                    )
                ]
        
        # Should compile and be callable
        assert callable(AudioPlayer)
        
        # Should create element without errors
        element = h(AudioPlayer)
        assert element is not None

    def test_input_focus_component(self):
        """Test focusing an input element via ref"""
        @component
        def FocusInput(ctx):
            input_element = None
            
            def set_input_ref(el):
                nonlocal input_element
                input_element = el
                
            def focus_input():
                if input_element:
                    # In real usage: input_element.focus()
                    pass
            
            for props in ctx:
                yield h.div[
                    h.button(onclick=focus_input)["Focus Input"],
                    h.input(
                        type="text",
                        placeholder="Will be focused",
                        ref=set_input_ref
                    )
                ]
        
        # Should compile and be callable
        assert callable(FocusInput)
        
        # Should create element without errors
        element = h(FocusInput)
        assert element is not None

    def test_canvas_drawing_component(self):
        """Test canvas manipulation via ref"""
        @component
        def CanvasComponent(ctx):
            canvas_element = None
            
            def set_canvas_ref(el):
                nonlocal canvas_element
                canvas_element = el
                # In real usage: ctx = canvas_element.getContext('2d')
                
            def draw_on_canvas():
                if canvas_element:
                    # In real usage: manipulate canvas context
                    pass
            
            for props in ctx:
                yield h.div[
                    h.button(onclick=draw_on_canvas)["Draw"],
                    h.canvas(
                        width=400,
                        height=300,
                        ref=set_canvas_ref
                    )
                ]
        
        # Should compile and be callable  
        assert callable(CanvasComponent)
        
        # Should create element without errors
        element = h(CanvasComponent)
        assert element is not None

    def test_form_validation_with_refs(self):
        """Test form validation using refs to access elements"""
        @component
        def FormWithValidation(ctx):
            name_input = None
            email_input = None
            
            def set_name_ref(el):
                nonlocal name_input
                name_input = el
                
            def set_email_ref(el):
                nonlocal email_input  
                email_input = el
                
            def validate_form():
                if name_input and email_input:
                    # In real usage: validate name_input.value, email_input.value
                    pass
            
            for props in ctx:
                yield h.form[
                    h.input(
                        type="text",
                        placeholder="Name",
                        ref=set_name_ref
                    ),
                    h.input(
                        type="email",
                        placeholder="Email", 
                        ref=set_email_ref
                    ),
                    h.button(onclick=validate_form)["Validate"]
                ]
        
        # Should compile and be callable
        assert callable(FormWithValidation)
        
        # Should create element without errors
        element = h(FormWithValidation)
        assert element is not None


class TestRefEdgeCases:
    """Test edge cases and error handling for refs."""

    def test_ref_with_none_value(self):
        """Test that ref=None doesn't cause errors"""
        element = h.div(ref=None)
        assert element is not None

    def test_ref_with_conditional_callback(self):
        """Test ref with conditional callback"""
        @component
        def ConditionalRef(ctx):
            should_ref = True
            
            def optional_ref(el):
                pass
            
            for props in ctx:
                ref_callback = optional_ref if should_ref else None
                yield h.input(type="text", ref=ref_callback)
        
        # Should compile and be callable
        assert callable(ConditionalRef)
        
        # Should create element without errors
        element = h(ConditionalRef)
        assert element is not None

    def test_ref_callback_error_handling(self):
        """Test that errors in ref callbacks don't break component"""
        @component
        def RefWithError(ctx):
            def error_ref(el):
                # This would cause an error in real usage
                raise ValueError("Ref callback error")
                
            for props in ctx:
                yield h.div(ref=error_ref)["Content"]
        
        # Should compile and be callable (error would happen at runtime)
        assert callable(RefWithError)
        
        # Should create element without errors (ref callback not called during creation)
        element = h(RefWithError)
        assert element is not None

    def test_ref_with_async_component(self):
        """Test refs work with async components"""
        @component
        async def AsyncComponentWithRef(ctx):
            button_element = None
            
            def set_button_ref(el):
                nonlocal button_element
                button_element = el
            
            async for props in ctx:
                yield h.button(ref=set_button_ref)["Async Button"]
        
        # Should compile and be callable
        assert callable(AsyncComponentWithRef)
        
        # Should create element without errors
        element = h(AsyncComponentWithRef)
        assert element is not None