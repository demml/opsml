def shipt_theme():
    background = "white"  # dark blue-grey
    grid = None  # lighter blue-grey
    text = "black"  # light grey
    font = "arial"
    fontsize = 12
    markcolor = "#241239"
    line_colors = [
        "#00ff41",  # matrix green
        "#241239",  # shipt purple
        "#f5d300",  # yellow
        "#00ff41",  # matrix green
        "#ff6c11",  # hot orange
        "#fd1d53",  # hot red
    ]

    return {
        "config": {
            "view": {"strokeWidth": 0},
            "background": background,
            "axis": {
                "gridColor": grid,
                "domainColor": "black",
                "tickColor": None,
                "labelColor": text,
                "titleColor": text,
                "titleFontSize": fontsize,
                "labelFontSize": fontsize,
            },
            "range": {"category": line_colors},
            "area": {"line": True, "fillOpacity": 0.1},
            "line": {"strokeWidth": 2},
            "bar": {
                "size": 15,
                "font": font,
                "labelFontSize": fontsize,
                "titleFontSize": fontsize,
                "fill": markcolor,
                "stroke": "#241239",
                "line": True,
                "fillOpacity": 0.5,
            },
        }
    }
