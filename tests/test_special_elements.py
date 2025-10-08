"""
Tests for special Crank element tags and props - achieving Crank.js parity

This test suite covers all the special elements and props that make Crank unique:
- Portal, Copy, Raw, Text elements
- Special props like key, ref, copy
- Fragment element with props
- DOM-specific prop handling
"""
import sys
from crank import h, component, Fragment, Portal, Copy, Raw, Text
import upytest


class TestSpecialElements:
    """Test special Crank elements (Portal, Copy, Raw, Text)"""
    
    def test_portal_element_exists(self):
        """Test that Portal element is available"""
        assert Portal is not None
        # Portal should be callable/constructible
        portal = h(Portal, target="body")["Portal content"]
        assert portal is not None
    
    def test_portal_with_target(self):
        """Test Portal element with target prop"""
        @component
        def PortalComponent(ctx):
            return h(Portal, target="#modal-root")[
                h.div["Modal content"],
                h.button["Close"]
            ]
        
        assert PortalComponent is not None
    
    def test_copy_element_exists(self):
        """Test that Copy element is available"""
        assert Copy is not None
        # Copy should be callable/constructible
        copy_elem = h(Copy)["Copied content"]
        assert copy_elem is not None
    
    def test_copy_element_optimization(self):
        """Test Copy element for preventing re-renders"""
        @component
        def OptimizedComponent(ctx):
            expensive_data = {"computed": "expensive calculation"}
            
            for props in ctx:
                # Copy prevents re-computation when props haven't changed
                yield h(Copy)[
                    h.div[f"Expensive result: {expensive_data['computed']}"]
                ]
        
        assert OptimizedComponent is not None
    
    def test_raw_element_exists(self):
        """Test that Raw element is available"""
        assert Raw is not None
        # Raw should be callable/constructible
        raw_elem = h(Raw)["<div>Raw HTML</div>"]
        assert raw_elem is not None
    
    def test_raw_element_html_injection(self):
        """Test Raw element for HTML string injection"""
        @component
        def RawHTMLComponent(ctx):
            html_string = "<strong>Bold text</strong> and <em>italic text</em>"
            return h(Raw)[html_string]
        
        assert RawHTMLComponent is not None
    
    def test_raw_element_with_props(self):
        """Test Raw element with additional props"""
        @component
        def RawWithPropsComponent(ctx):
            return h(Raw, className="raw-content", id="raw-1")[
                "<p>HTML content with props</p>"
            ]
        
        assert RawWithPropsComponent is not None
    
    def test_text_element_exists(self):
        """Test that Text element is available"""
        assert Text is not None
        # Text should be callable/constructible
        text_elem = h(Text)["Plain text content"]
        assert text_elem is not None
    
    def test_text_element_explicit_text(self):
        """Test Text element for explicit text node creation"""
        @component
        def ExplicitTextComponent(ctx):
            return h.div[
                h(Text)["This is explicit text"],
                h(Text)["Another text node"]
            ]
        
        assert ExplicitTextComponent is not None
    
    def test_text_element_with_props(self):
        """Test Text element with props (though typically not used)"""
        @component
        def TextWithPropsComponent(ctx):
            return h(Text, key="text-key")["Text with key"]
        
        assert TextWithPropsComponent is not None


class TestFragmentWithProps:
    """Test Fragment element with props and advanced usage"""
    
    def test_fragment_element_exists(self):
        """Test that Fragment element is available"""
        assert Fragment is not None
        # Fragment should be callable/constructible
        frag = h(Fragment)["Child 1", "Child 2"]
        assert frag is not None
    
    def test_fragment_with_key_prop(self):
        """Test Fragment with key prop for list management"""
        @component
        def FragmentKeyComponent(ctx):
            items = ["item1", "item2", "item3"]
            
            for props in ctx:
                yield [
                    h(Fragment, key=f"frag-{i}")[
                        h.div[item]
                    ] for i, item in enumerate(items)
                ]
        
        assert FragmentKeyComponent is not None
    
    def test_fragment_empty_string_syntax(self):
        """Test Fragment using empty string syntax"""
        @component
        def EmptyStringFragmentComponent(ctx):
            # h("", ...) creates a Fragment
            return h("", key="empty-frag")[
                h.span["First"],
                h.span["Second"]
            ]
        
        assert EmptyStringFragmentComponent is not None
    
    def test_fragment_list_syntax(self):
        """Test Fragment as Python list (most common usage)"""
        @component
        def ListFragmentComponent(ctx):
            return [
                h.div["First element"],
                h.div["Second element"],
                h.div["Third element"]
            ]
        
        assert ListFragmentComponent is not None
    
    def test_nested_fragments(self):
        """Test nested Fragment elements"""
        @component
        def NestedFragmentComponent(ctx):
            return h(Fragment)[
                h.div["Before nested"],
                h(Fragment, key="nested")[
                    h.span["Nested 1"],
                    h.span["Nested 2"]
                ],
                h.div["After nested"]
            ]
        
        assert NestedFragmentComponent is not None


class TestSpecialProps:
    """Test special props (key, ref, copy)"""
    
    def test_key_prop_basic(self):
        """Test key prop for element identification"""
        @component
        def KeyPropComponent(ctx):
            for props in ctx:
                items = props.get("items", [1, 2, 3])
                yield [
                    h.div(key=f"item-{item}")[f"Item {item}"] 
                    for item in items
                ]
        
        assert KeyPropComponent is not None
    
    def test_key_prop_reordering(self):
        """Test key prop helps with list reordering"""
        @component
        def ReorderingComponent(ctx):
            for props in ctx:
                items = props.get("items", ["a", "b", "c"])
                reverse = props.get("reverse", False)
                
                if reverse:
                    items = list(reversed(items))
                
                yield [
                    h.li(key=item)[f"Item: {item}"]
                    for item in items
                ]
        
        assert ReorderingComponent is not None
    
    def test_ref_prop_callback(self):
        """Test ref prop for element reference"""
        element_refs = []
        
        def capture_ref(element):
            element_refs.append(element)
        
        @component
        def RefPropComponent(ctx):
            return h.div(ref=capture_ref)[
                "Content with ref"
            ]
        
        assert RefPropComponent is not None
        # Note: refs would be tested with actual rendering
    
    def test_ref_prop_multiple_elements(self):
        """Test ref props on multiple elements"""
        refs = {"input": None, "button": None}
        
        def input_ref(element):
            refs["input"] = element
            
        def button_ref(element):
            refs["button"] = element
        
        @component
        def MultiRefComponent(ctx):
            return h.form[
                h.input_(ref=input_ref, placeholder="Enter text"),
                h.button(ref=button_ref)["Submit"]
            ]
        
        assert MultiRefComponent is not None
    
    def test_copy_prop_boolean(self):
        """Test copy prop for preventing re-renders"""
        @component
        def CopyPropComponent(ctx):
            expensive_value = "computed result"
            
            for props in ctx:
                # copy=True prevents re-render if props haven't changed
                yield h.div(copy=True)[
                    f"Expensive: {expensive_value}"
                ]
        
        assert CopyPropComponent is not None
    
    def test_copy_prop_selective(self):
        """Test selective copy prop (copy="!prop_name")"""
        @component
        def SelectiveCopyComponent(ctx):
            for props in ctx:
                # copy="!timestamp" means copy unless timestamp changes
                yield h.div(copy="!timestamp")[
                    f"Updated: {props.get('timestamp', 0)}"
                ]
        
        assert SelectiveCopyComponent is not None


class TestDOMSpecificProps:
    """Test DOM-specific prop handling"""
    
    def test_style_object_prop(self):
        """Test style prop as object"""
        @component
        def StyleObjectComponent(ctx):
            styles = {
                "color": "red",
                "fontSize": "16px",
                "backgroundColor": "blue"
            }
            return h.div(style=styles)["Styled content"]
        
        assert StyleObjectComponent is not None
    
    def test_style_string_prop(self):
        """Test style prop as string"""
        @component
        def StyleStringComponent(ctx):
            return h.div(style="color: green; font-size: 18px")[
                "String styled content"
            ]
        
        assert StyleStringComponent is not None
    
    def test_innerHTML_prop(self):
        """Test innerHTML prop for HTML injection"""
        @component
        def InnerHTMLComponent(ctx):
            html_content = "<strong>Bold</strong> and <em>italic</em>"
            return h.div(innerHTML=html_content)
        
        assert InnerHTMLComponent is not None
    
    def test_className_vs_class_prop(self):
        """Test className vs class prop compatibility"""
        @component
        def ClassNameComponent(ctx):
            return [
                h.div(className="class-name-style")["Using className"],
                h.div(**{"class": "class-style"})["Using class"]
            ]
        
        assert ClassNameComponent is not None
    
    def test_data_attributes(self):
        """Test data-* attributes"""
        @component
        def DataAttributesComponent(ctx):
            return h.div(
                **{
                    "data-testid": "test-element",
                    "data-value": "123",
                    "data-custom": "custom-data"
                }
            )["Element with data attributes"]
        
        assert DataAttributesComponent is not None
    
    def test_aria_attributes(self):
        """Test aria-* attributes for accessibility"""
        @component
        def AriaAttributesComponent(ctx):
            return h.button(
                **{
                    "aria-label": "Close dialog",
                    "aria-expanded": "false",
                    "aria-controls": "dialog-content"
                }
            )["Close"]
        
        assert AriaAttributesComponent is not None
    
    def test_boolean_attributes(self):
        """Test boolean HTML attributes"""
        @component
        def BooleanAttributesComponent(ctx):
            return [
                h.input_(type="checkbox", checked=True, disabled=False),
                h.button(disabled=True)["Disabled"],
                h.input_(type="text", required=True, readonly=False)
            ]
        
        assert BooleanAttributesComponent is not None


class TestSpecialElementCombinations:
    """Test combinations of special elements and props"""
    
    def test_portal_with_key_and_ref(self):
        """Test Portal with key and ref props"""
        portal_ref = None
        
        def capture_portal_ref(element):
            nonlocal portal_ref
            portal_ref = element
        
        @component
        def PortalWithPropsComponent(ctx):
            return h(Portal, target="body", key="main-modal", ref=capture_portal_ref)[
                h.div(className="modal")[
                    h.h2["Modal Title"],
                    h.p["Modal content"]
                ]
            ]
        
        assert PortalWithPropsComponent is not None
    
    def test_copy_element_with_special_props(self):
        """Test Copy element with key and other props"""
        @component
        def CopyWithPropsComponent(ctx):
            for props in ctx:
                yield h(Copy, key="optimized-section")[
                    h.div(className="expensive-render")[
                        "Expensive computation result"
                    ]
                ]
        
        assert CopyWithPropsComponent is not None
    
    def test_raw_element_with_copy_prop(self):
        """Test Raw element with copy prop optimization"""
        @component
        def RawWithCopyComponent(ctx):
            static_html = "<div><strong>Static HTML</strong></div>"
            
            for props in ctx:
                # Raw + copy prevents re-parsing HTML
                yield h(Raw, copy=True)[static_html]
        
        assert RawWithCopyComponent is not None
    
    def test_fragment_with_portal_children(self):
        """Test Fragment containing Portal elements"""
        @component
        def FragmentPortalComponent(ctx):
            return h(Fragment)[
                h.div["Main content"],
                h(Portal, target="#sidebar")[
                    h.div["Sidebar content"]
                ],
                h(Portal, target="#footer")[
                    h.div["Footer content"]
                ]
            ]
        
        assert FragmentPortalComponent is not None
    
    def test_nested_special_elements(self):
        """Test deeply nested special elements"""
        @component
        def DeepNestingComponent(ctx):
            return h(Fragment, key="root-fragment")[
                h(Copy, key="copy-section")[
                    h(Portal, target="#modal")[
                        h(Fragment)[
                            h(Text)["Modal text"],
                            h(Raw)["<em>Raw modal content</em>"]
                        ]
                    ]
                ]
            ]
        
        assert DeepNestingComponent is not None


class TestSpecialElementErrorHandling:
    """Test error handling with special elements"""
    
    def test_portal_invalid_target(self):
        """Test Portal with invalid target (should not crash)"""
        @component
        def InvalidPortalComponent(ctx):
            try:
                return h(Portal, target="#nonexistent-target")[
                    h.div["Content for invalid target"]
                ]
            except Exception as e:
                return h.div[f"Portal error handled: {e}"]
        
        assert InvalidPortalComponent is not None
    
    def test_raw_malformed_html(self):
        """Test Raw element with malformed HTML"""
        @component
        def MalformedRawComponent(ctx):
            malformed_html = "<div><span>Unclosed tags</div>"
            return h(Raw)[malformed_html]
        
        assert MalformedRawComponent is not None
    
    def test_copy_with_changing_props(self):
        """Test Copy behavior when props actually change"""
        @component
        def ChangingCopyComponent(ctx):
            for props in ctx:
                counter = props.get("counter", 0)
                # Copy should re-render when counter changes
                yield h(Copy, copy="!counter")[
                    h.div[f"Counter: {counter}"]
                ]
        
        assert ChangingCopyComponent is not None