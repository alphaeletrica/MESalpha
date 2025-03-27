class Themes:
    LIGHT = {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#C0C0C0',
        'text_primary': '#000000',
        'text_secondary': '#666666',
        'button_bg': '#C8C8C8',
        'button_hover': '#B8B8B8',
        'button_text': '#000000',
        'accent': '#A0A0A0',
        'hover': '#B8B8B8',
        'active': '#909090',
        'bg_card': '#F0F0F0',
        'border': '#D0D0D0',
        'success': '#28A745',
        'red': '#FF0000',
        'red_hover': '#E60000',
        'card_radius': '10px'
    }
    DARK = {
        'bg_primary': '#2B2B2B',
        'bg_secondary': '#3C3C3C',
        'text_primary': '#FFFFFF',
        'text_secondary': '#BBBBBB',
        'button_bg': '#3A3A3A',
        'button_hover': '#4A4A4A',
        'button_text': '#FFFFFF',
        'accent': '#5A5A5A',
        'hover': '#4A4A4A',
        'active': '#6A6A6A',
        'bg_card': '#3C3C3C',
        'border': '#505050',
        'success': '#34CE57',
        'red': '#FF0000',
        'red_hover': '#E60000',
        'card_radius': '10px'
    }
    
def get_stylesheet(theme):
    return f"""
        QMainWindow, QWidget#dashboardContainer {{
            background-color: {theme['bg_primary']};
        }}
        #header {{
            background-color: {theme['bg_secondary']};
        }}
        #sidebar {{
            background-color: {theme['bg_secondary']};
        }}
        #navButton, #toggleButton {{
            background-color: {theme['button_bg']};
            color: {theme['button_text']};
            border: none;
            padding: 10px;
            text-align: left;
        }}
        #navButton:hover, #toggleButton:hover {{
            background-color: {theme['button_hover']};
        }}
        #themeButton {{
            background-color: {theme['button_bg']};
            border: none;
        }}
        #themeButton:hover {{
            background-color: {theme['button_hover']};
        }}
        QLabel {{
            color: {theme['text_primary']};
            background-color: transparent;
        }}
    """