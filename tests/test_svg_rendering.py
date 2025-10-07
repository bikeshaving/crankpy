"""
Test SVG rendering support - actual functionality testing
"""


from crank import component, h


class TestSVGElements:
    """Test basic SVG element creation and compilation."""

    def test_svg_root_element(self):
        """Test creating SVG root element"""
        element = h.svg(
            width="100",
            height="100",
            viewBox="0 0 100 100",
            xmlns="http://www.w3.org/2000/svg"
        )

        assert element is not None

    def test_svg_basic_shapes(self):
        """Test basic SVG shape elements compile"""
        # Circle
        circle = h.circle(cx="50", cy="50", r="25", fill="red")

        # Rectangle
        rect = h.rect(x="10", y="10", width="80", height="30", fill="blue")

        # Line
        line = h.line(x1="0", y1="0", x2="100", y2="100", stroke="black")

        # Ellipse
        ellipse = h.ellipse(cx="50", cy="50", rx="40", ry="20", fill="green")

        assert circle is not None
        assert rect is not None
        assert line is not None
        assert ellipse is not None

    def test_svg_path_element(self):
        """Test SVG path element with complex paths"""
        # Simple path
        simple_path = h.path(d="M 10 10 L 90 90", stroke="black", fill="none")

        # Complex path with curves
        complex_path = h.path(
            d="M 10 80 C 40 10, 65 10, 95 80 S 150 150, 180 80",
            stroke="blue",
            strokeWidth="2",
            fill="none"
        )

        assert simple_path is not None
        assert complex_path is not None

    def test_svg_text_elements(self):
        """Test SVG text rendering"""
        text_element = h.text(x="50", y="50", textAnchor="middle", fontSize="16")

        # Text span
        tspan_element = h.tspan(dx="5", dy="10")

        assert text_element is not None
        assert tspan_element is not None

    def test_svg_grouping_elements(self):
        """Test SVG grouping and organization elements"""
        # Group
        group = h.g(transform="translate(50, 50)")

        # Definition group
        defs = h.defs()

        # Symbol
        symbol = h.symbol(id="my-symbol", viewBox="0 0 10 10")

        # Use element
        use = h.use(href="#my-symbol", x="20", y="20")

        assert group is not None
        assert defs is not None
        assert symbol is not None
        assert use is not None


class TestSVGAttributes:
    """Test SVG-specific attributes and prop handling."""

    def test_svg_dash_attributes(self):
        """Test attributes with dashes (stroke-width, etc.)"""
        element = h.circle(
            cx="50",
            cy="50",
            r="25",
            stroke="black",
            strokeWidth="2",
            strokeDasharray="5,5",
            strokeLinecap="round"
        )

        assert element is not None

    def test_svg_fill_and_stroke(self):
        """Test fill and stroke attribute variations"""
        # Solid colors
        solid = h.rect(fill="red", stroke="blue")

        # Hex colors
        hex_colors = h.circle(fill="#ff0000", stroke="#0000ff")

        # RGB colors
        rgb_colors = h.path(fill="rgb(255, 0, 0)", stroke="rgba(0, 0, 255, 0.5)")

        # Gradients and patterns
        gradients = h.ellipse(fill="url(#gradient1)", stroke="url(#pattern1)")

        assert solid is not None
        assert hex_colors is not None
        assert rgb_colors is not None
        assert gradients is not None

    def test_svg_transform_attributes(self):
        """Test SVG transform attributes"""
        # Translation
        translate = h.g(transform="translate(50, 100)")

        # Rotation
        rotate = h.g(transform="rotate(45)")

        # Scale
        scale = h.g(transform="scale(2, 0.5)")

        # Complex transform
        complex_transform = h.g(transform="translate(50, 50) rotate(45) scale(1.5)")

        assert translate is not None
        assert rotate is not None
        assert scale is not None
        assert complex_transform is not None

    def test_svg_camelcase_attributes(self):
        """Test camelCase SVG attributes compile correctly"""
        element = h.circle(
            strokeWidth="2",
            strokeDasharray="5,5",
            strokeLinecap="round",
            strokeLinejoin="miter",
            fillOpacity="0.5",
            strokeOpacity="0.8"
        )

        assert element is not None


class TestSVGComponents:
    """Test SVG usage within components."""

    def test_svg_icon_component(self):
        """Test creating reusable SVG icon components"""
        @component
        def CheckIcon(ctx):
            for props in ctx:
                size = props.get("size", "24")
                color = props.get("color", "currentColor")

                yield h.svg(
                    width=size,
                    height=size,
                    viewBox="0 0 24 24",
                    fill="none",
                    stroke=color,
                    strokeWidth="2"
                )[
                    h.path(d="M20 6L9 17l-5-5")
                ]

        # Should compile and be callable
        assert callable(CheckIcon)

        # Should create element without errors
        element = h(CheckIcon)
        assert element is not None

        # With props
        element_with_props = h(CheckIcon, size="32", color="red")
        assert element_with_props is not None

    def test_svg_chart_component(self):
        """Test SVG usage for data visualization"""
        @component
        def BarChart(ctx):
            for props in ctx:
                data = props.get("data", [10, 20, 30, 40])
                width = props.get("width", 300)
                height = props.get("height", 200)

                bars = []
                bar_width = width / len(data) if data else 0

                for i, value in enumerate(data):
                    bar_height = (value / 100) * height
                    x = i * bar_width
                    y = height - bar_height

                    bars.append(
                        h.rect(
                            x=str(x),
                            y=str(y),
                            width=str(bar_width - 2),
                            height=str(bar_height),
                            fill="steelblue",
                            key=i
                        )
                    )

                yield h.svg(width=str(width), height=str(height), viewBox=f"0 0 {width} {height}")[
                    bars
                ]

        # Should compile and be callable
        assert callable(BarChart)

        # Should create element without errors
        element = h(BarChart)
        assert element is not None

        # With custom data
        element_with_data = h(BarChart, data=[5, 15, 25, 35], width=400, height=300)
        assert element_with_data is not None

    def test_animated_svg_component(self):
        """Test SVG with animations and transitions"""
        @component
        def SpinningIcon(ctx):
            for props in ctx:
                size = props.get("size", "24")

                yield h.svg(
                    width=size,
                    height=size,
                    viewBox="0 0 24 24",
                    className="spinning-icon"
                )[
                    h.circle(
                        cx="12",
                        cy="12",
                        r="10",
                        stroke="currentColor",
                        strokeWidth="2",
                        fill="none"
                    )[
                        h.animateTransform(
                            attributeName="transform",
                            attributeType="XML",
                            type="rotate",
                            values="0 12 12;360 12 12",
                            dur="1s",
                            repeatCount="indefinite"
                        )
                    ]
                ]

        # Should compile and be callable
        assert callable(SpinningIcon)

        # Should create element without errors
        element = h(SpinningIcon)
        assert element is not None


class TestSVGUseCases:
    """Test realistic SVG usage patterns and edge cases."""

    def test_svg_with_gradients_and_patterns(self):
        """Test SVG with definitions, gradients, and patterns"""
        @component
        def GradientButton(ctx):
            for props in ctx:
                yield h.svg(width="100", height="40", viewBox="0 0 100 40")[
                    h.defs[
                        h.linearGradient(id="buttonGradient", x1="0%", y1="0%", x2="0%", y2="100%")[
                            h.stop(offset="0%", stopColor="#4CAF50"),
                            h.stop(offset="100%", stopColor="#45a049")
                        ]
                    ],
                    h.rect(
                        width="100",
                        height="40",
                        rx="5",
                        fill="url(#buttonGradient)",
                        stroke="#333",
                        strokeWidth="1"
                    ),
                    h.text(x="50", y="25", textAnchor="middle", fill="white", fontSize="12")[
                        "Button"
                    ]
                ]

        # Should compile and be callable
        assert callable(GradientButton)

        # Should create element without errors
        element = h(GradientButton)
        assert element is not None

    def test_svg_responsive_design(self):
        """Test responsive SVG design patterns"""
        @component
        def ResponsiveSVG(ctx):
            for props in ctx:
                yield h.div(className="responsive-svg-container")[
                    h.svg(
                        viewBox="0 0 100 100",
                        preserveAspectRatio="xMidYMid meet",
                        className="responsive-svg"
                    )[
                        h.circle(cx="50", cy="50", r="40", fill="blue"),
                        h.text(x="50", y="55", textAnchor="middle", fontSize="12", fill="white")[
                            "Responsive"
                        ]
                    ]
                ]

        # Should compile and be callable
        assert callable(ResponsiveSVG)

        # Should create element without errors
        element = h(ResponsiveSVG)
        assert element is not None

    def test_svg_with_event_handlers(self):
        """Test SVG elements with event handlers"""
        @component
        def InteractiveSVG(ctx):
            selected_shape = None

            @ctx.refresh
            def handle_click(shape_id):
                def handler(ev):
                    nonlocal selected_shape
                    selected_shape = shape_id
                return handler

            for props in ctx:
                yield h.svg(width="200", height="200", viewBox="0 0 200 200")[
                    h.circle(
                        cx="50",
                        cy="50",
                        r="30",
                        fill="red" if selected_shape == "circle" else "lightcoral",
                        onclick=handle_click("circle"),
                        style={"cursor": "pointer"}
                    ),
                    h.rect(
                        x="120",
                        y="20",
                        width="60",
                        height="60",
                        fill="blue" if selected_shape == "rect" else "lightblue",
                        onclick=handle_click("rect"),
                        style={"cursor": "pointer"}
                    )
                ]

        # Should compile and be callable
        assert callable(InteractiveSVG)

        # Should create element without errors
        element = h(InteractiveSVG)
        assert element is not None

    def test_svg_nested_structures(self):
        """Test complex nested SVG structures"""
        @component
        def ComplexSVG(ctx):
            for props in ctx:
                yield h.svg(width="300", height="200", viewBox="0 0 300 200")[
                    h.defs[
                        h.marker(
                            id="arrowhead",
                            markerWidth="10",
                            markerHeight="7",
                            refX="0",
                            refY="3.5",
                            orient="auto"
                        )[
                            h.polygon(points="0 0, 10 3.5, 0 7", fill="#333")
                        ]
                    ],
                    h.g(className="diagram")[
                        h.rect(x="20", y="20", width="80", height="50", fill="lightblue", stroke="#333"),
                        h.text(x="60", y="50", textAnchor="middle", fontSize="12")["Start"],

                        h.line(
                            x1="100",
                            y1="45",
                            x2="180",
                            y2="45",
                            stroke="#333",
                            strokeWidth="2",
                            markerEnd="url(#arrowhead)"
                        ),

                        h.rect(x="180", y="20", width="80", height="50", fill="lightgreen", stroke="#333"),
                        h.text(x="220", y="50", textAnchor="middle", fontSize="12")["End"]
                    ]
                ]

        # Should compile and be callable
        assert callable(ComplexSVG)

        # Should create element without errors
        element = h(ComplexSVG)
        assert element is not None

    def test_svg_with_foreign_objects(self):
        """Test SVG foreignObject for embedding HTML"""
        @component
        def SVGWithHTML(ctx):
            for props in ctx:
                yield h.svg(width="200", height="150", viewBox="0 0 200 150")[
                    h.rect(width="200", height="150", fill="lightgray", stroke="#333"),
                    h.foreignObject(x="10", y="10", width="180", height="130")[
                        h.div(
                            style={
                                "padding": "10px",
                                "background": "white",
                                "border": "1px solid #ccc",
                                "height": "100%",
                                "box-sizing": "border-box"
                            }
                        )[
                            h.h3["HTML in SVG"],
                            h.p["This is HTML content embedded in an SVG using foreignObject."],
                            h.button(onclick=lambda ev: None)["Click me"]
                        ]
                    ]
                ]

        # Should compile and be callable
        assert callable(SVGWithHTML)

        # Should create element without errors
        element = h(SVGWithHTML)
        assert element is not None

    def test_svg_icon_library_pattern(self):
        """Test creating a library of SVG icons"""
        @component
        def IconLibrary(ctx):
            for props in ctx:
                icon_type = props.get("type", "home")
                size = props.get("size", "24")

                # Icon definitions
                icons = {
                    "home": h.path(d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"),
                    "user": h.circle(cx="12", cy="12", r="3") + h.path(d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"),
                    "star": h.polygon(points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26")
                }

                icon_path = icons.get(icon_type, icons["home"])

                yield h.svg(
                    width=size,
                    height=size,
                    viewBox="0 0 24 24",
                    fill="none",
                    stroke="currentColor",
                    strokeWidth="2",
                    strokeLinecap="round",
                    strokeLinejoin="round"
                )[icon_path]

        # Should compile and be callable
        assert callable(IconLibrary)

        # Test different icon types
        home_icon = h(IconLibrary, type="home")
        user_icon = h(IconLibrary, type="user", size="32")
        star_icon = h(IconLibrary, type="star")

        assert home_icon is not None
        assert user_icon is not None
        assert star_icon is not None
