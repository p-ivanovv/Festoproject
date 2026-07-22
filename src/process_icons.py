import os
import re

def process_fluent_icons():
    assets_dir = 'src/assets'
    os.makedirs(assets_dir, exist_ok=True)

    chev_file = os.path.join(assets_dir, 'chevron_down.svg')
    if os.path.exists(chev_file):
        with open(chev_file, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Replace fill="212121" or fill="#212121" with light color #A0A0A8
        light_svg = re.sub(r'fill="[^"]*"', 'fill="#A0A0A8"', svg_content)
        if 'fill="#A0A0A8"' not in light_svg:
            light_svg = re.sub(r'<path ', r'<path fill="#A0A0A8" ', light_svg)
        with open(os.path.join(assets_dir, 'chevron_down_light.svg'), 'w', encoding='utf-8') as f:
            f.write(light_svg)

        # Replace fill with hover color #0078F2
        hover_svg = re.sub(r'fill="[^"]*"', 'fill="#0078F2"', svg_content)
        if 'fill="#0078F2"' not in hover_svg:
            hover_svg = re.sub(r'<path ', r'<path fill="#0078F2" ', hover_svg)
        with open(os.path.join(assets_dir, 'chevron_down_hover.svg'), 'w', encoding='utf-8') as f:
            f.write(hover_svg)

        print("Processed chevron_down dropdown light and hover icons properly.")

if __name__ == "__main__":
    process_fluent_icons()
