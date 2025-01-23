import os
import re
import shutil

CLI_BOXES = {
    "single": {
        "topLeft": "┌",
        "top": "─",
        "topRight": "┐",
        "right": "│",
        "bottomRight": "┘",
        "bottom": "─",
        "bottomLeft": "└",
        "left": "│",
    },
    "double": {
        "topLeft": "╔",
        "top": "═",
        "topRight": "╗",
        "right": "║",
        "bottomRight": "╝",
        "bottom": "═",
        "bottomLeft": "╚",
        "left": "║",
    },
    "round": {
        "topLeft": "╭",
        "top": "─",
        "topRight": "╮",
        "right": "│",
        "bottomRight": "╯",
        "bottom": "─",
        "bottomLeft": "╰",
        "left": "│",
    },
    "bold": {
        "topLeft": "┏",
        "top": "━",
        "topRight": "┓",
        "right": "┃",
        "bottomRight": "┛",
        "bottom": "━",
        "bottomLeft": "┗",
        "left": "┃",
    },
    "none": {
        "topLeft": "",
        "top": "",
        "topRight": "",
        "right": "",
        "bottomRight": "",
        "bottom": "",
        "bottomLeft": "",
        "left": "",
    },
}


def terminal_columns():
    try:
        return shutil.get_terminal_size().columns
    except OSError:
        return 80


def get_object(detail):
    if isinstance(detail, int):
        return {
            "top": detail,
            "right": detail * 3,
            "bottom": detail,
            "left": detail * 3,
        }
    else:
        defaults = {"top": 0, "right": 0, "bottom": 0, "left": 0}
        if detail:
            defaults.update(detail)
        return defaults


def get_border_width(border_style):
    return 0 if border_style == "none" else 2


def get_border_chars(border_style):
    sides = [
        "topLeft",
        "topRight",
        "bottomRight",
        "bottomLeft",
        "left",
        "right",
        "top",
        "bottom",
    ]
    if border_style == "none":
        return {side: "" for side in sides}
    if isinstance(border_style, str):
        if border_style not in CLI_BOXES:
            raise ValueError(f"Invalid border style: {border_style}")
        return CLI_BOXES[border_style].copy()
    else:
        border_style = border_style.copy()
        if "vertical" in border_style:
            border_style["left"] = border_style["vertical"]
            border_style["right"] = border_style["vertical"]
        if "horizontal" in border_style:
            border_style["top"] = border_style["horizontal"]
            border_style["bottom"] = border_style["horizontal"]
        for side in sides:
            if side not in border_style or not isinstance(border_style[side], str):
                raise ValueError(
                    f"Invalid border style: {side} is missing or not a string"
                )
        return border_style


def string_width(s):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return len(ansi_escape.sub("", s))


def wrap_ansi(text, width):
    ansi_escape = re.compile(r"(\x1B\[[0-?]*[ -/]*[@-~])")
    chunks = []
    current_chunk = []
    current_length = 0

    for part in ansi_escape.split(text):
        if ansi_escape.match(part):
            current_chunk.append(part)
        else:
            words = part.split(" ")
            for word in words:
                word_length = len(word)
                if current_length + word_length > width:
                    chunks.append("".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                current_chunk.append(word + " ")
                current_length += word_length + 1
    if current_chunk:
        chunks.append("".join(current_chunk).strip())
    return "\n".join(chunks)


def ansi_align(text, align):
    lines = text.split("\n")
    max_width = max(string_width(line) for line in lines) if lines else 0
    aligned = []
    for line in lines:
        line_width = string_width(line)
        if align == "center":
            pad_left = (max_width - line_width) // 2
            pad_right = max_width - line_width - pad_left
            aligned_line = " " * pad_left + line + " " * pad_right
        elif align == "right":
            pad_left = max_width - line_width
            aligned_line = " " * pad_left + line
        else:
            pad_right = max_width - line_width
            aligned_line = line + " " * pad_right
        aligned.append(aligned_line)
    return "\n".join(aligned)


def make_title(text, horizontal, alignment):
    text_width = string_width(text)
    content_width = len(horizontal)
    remaining_space = content_width - text_width
    if remaining_space < 0:
        return horizontal
    if alignment == "left":
        return text + horizontal[text_width:]
    elif alignment == "right":
        return horizontal[:remaining_space] + text
    else:
        left_pad = remaining_space // 2
        right_pad = remaining_space - left_pad
        return horizontal[:left_pad] + text + horizontal[content_width - right_pad :]


def make_content_text(text, options):
    padding = options["padding"]
    width = options["width"]
    text_alignment = options["textAlignment"]
    height = options.get("height")

    content_width = width - padding["left"] - padding["right"]
    processed_lines = []

    for line in text.split("\n"):
        wrapped = wrap_ansi(line, content_width)
        for wrapped_line in wrapped.split("\n"):
            visible_length = string_width(wrapped_line)
            total_space = content_width - visible_length

            # Preserve ANSI sequence integrity
            if text_alignment == "center":
                left_pad = " " * (total_space // 2)
                right_pad = " " * (total_space - total_space // 2)
                aligned = f"{left_pad}{wrapped_line}{right_pad}"
            elif text_alignment == "right":
                aligned = f"{' ' * total_space}{wrapped_line}"
            else:
                aligned = f"{wrapped_line}{' ' * total_space}"

            # Add padding with ANSI preservation
            full_line = (
                " " * padding["left"] + aligned + " " * padding["right"]
            ).ljust(width)
            processed_lines.append(full_line)

    # Rest of vertical padding and height handling remains the same
    if padding["top"] > 0:
        processed_lines = [" " * width] * padding["top"] + processed_lines
    if padding["bottom"] > 0:
        processed_lines += [" " * width] * padding["bottom"]

    if height is not None:
        if len(processed_lines) > height:
            processed_lines = processed_lines[:height]
        else:
            processed_lines += [" " * width] * (height - len(processed_lines))

    return "\n".join(processed_lines)


def is_hex(color):
    return re.match(r"^#([0-9a-fA-F]{3}){1,2}$", color)


def is_color_valid(color):
    known_colors = {
        "black",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
        "gray",
        "grey",
        "brightRed",
        "brightGreen",
        "brightYellow",
        "brightBlue",
        "brightMagenta",
        "brightCyan",
        "brightWhite",
    }
    return color.lower() in known_colors or is_hex(color)


def apply_color(text, color):
    if is_hex(color):
        hex_color = color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"\x1b[38;2;{r};{g};{b}m{text}\x1b[0m"
    else:
        color_map = {
            "black": "\x1b[30m",
            "red": "\x1b[31m",
            "green": "\x1b[32m",
            "yellow": "\x1b[33m",
            "blue": "\x1b[34m",
            "magenta": "\x1b[35m",
            "cyan": "\x1b[36m",
            "white": "\x1b[37m",
            "gray": "\x1b[90m",
            "grey": "\x1b[90m",
            "brightRed": "\x1b[91m",
            "brightGreen": "\x1b[92m",
            "brightYellow": "\x1b[93m",
            "brightBlue": "\x1b[94m",
            "brightMagenta": "\x1b[95m",
            "brightCyan": "\x1b[96m",
            "brightWhite": "\x1b[97m",
        }
        code = color_map.get(color.lower(), "")
        return f"{code}{text}\x1b[0m"


def apply_bg_color(text, color):
    if is_hex(color):
        hex_color = color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"\x1b[48;2;{r};{g};{b}m{text}\x1b[0m"
    else:
        color_map = {
            "black": "\x1b[40m",
            "red": "\x1b[41m",
            "green": "\x1b[42m",
            "yellow": "\x1b[43m",
            "blue": "\x1b[44m",
            "magenta": "\x1b[45m",
            "cyan": "\x1b[46m",
            "white": "\x1b[47m",
            "gray": "\x1b[100m",
            "grey": "\x1b[100m",
            "brightRed": "\x1b[101m",
            "brightGreen": "\x1b[102m",
            "brightYellow": "\x1b[103m",
            "brightBlue": "\x1b[104m",
            "brightMagenta": "\x1b[105m",
            "brightCyan": "\x1b[106m",
            "brightWhite": "\x1b[107m",
        }
        code = color_map.get(color.lower(), "")
        return f"{code}{text}\x1b[0m"


def dim_text(text):
    return f"\x1b[2m{text}\x1b[0m"


def sanitize_options(options):
    options = options.copy()
    if options.get("fullscreen"):
        try:
            columns, rows = os.get_terminal_size()
        except (OSError, ValueError):
            columns, rows = 80, 24
        if callable(options["fullscreen"]):
            new_columns, new_rows = options["fullscreen"](columns, rows)
        else:
            new_columns, new_rows = columns, rows
        if "width" not in options:
            options["width"] = new_columns
        if "height" not in options:
            options["height"] = new_rows
    if "width" in options:
        options["width"] = max(
            1, options["width"] - get_border_width(options.get("borderStyle", "single"))
        )
    if "height" in options:
        options["height"] = max(
            1,
            options["height"] - get_border_width(options.get("borderStyle", "single")),
        )
    return options


def format_title(title, border_style):
    if border_style == "none":
        return title
    else:
        return f" {title} "


def determine_dimensions(text, options):
    options = sanitize_options(options.copy())
    width_override = "width" in options
    columns = terminal_columns()
    border_style = options.get("borderStyle", "single")
    border_width = get_border_width(border_style)
    max_width = (
        columns - options["margin"]["left"] - options["margin"]["right"] - border_width
    )

    wrapped_text = wrap_ansi(text, columns - border_width)
    widest = max((string_width(line) for line in wrapped_text.split("\n")), default=0)
    widest += options["padding"]["left"] + options["padding"]["right"]

    if options.get("title"):
        title = options["title"]
        if width_override:
            title = title[: max(0, options["width"] - 2)]
        else:
            title = title[: max(0, max_width - 2)]
        if title:
            formatted_title = format_title(title, border_style)
            options["title"] = formatted_title
            title_width = string_width(formatted_title)
            if not width_override and title_width > widest:
                options["width"] = title_width

    if not width_override:
        options["width"] = widest

    if not width_override:
        available_space = columns - options["width"] - border_width
        margin_left = options["margin"]["left"]
        margin_right = options["margin"]["right"]
        total_margin = margin_left + margin_right
        if total_margin > 0 and available_space < total_margin:
            ratio = available_space / total_margin
            options["margin"]["left"] = max(0, int(margin_left * ratio))
            options["margin"]["right"] = max(0, int(margin_right * ratio))
        options["width"] = min(
            options["width"],
            columns
            - border_width
            - options["margin"]["left"]
            - options["margin"]["right"],
        )

    content_width = options["width"] - (
        options["padding"]["left"] + options["padding"]["right"]
    )
    if content_width <= 0:
        options["padding"]["left"] = 0
        options["padding"]["right"] = 0

    if "height" in options:
        content_height = options["height"] - (
            options["padding"]["top"] + options["padding"]["bottom"]
        )
        if content_height <= 0:
            options["padding"]["top"] = 0
            options["padding"]["bottom"] = 0

    return options


def box_content(content, content_width, options):
    border_color = options.get("borderColor")
    bg_color = options.get("backgroundColor")
    dim_border = options.get("dimBorder", False)
    border_style = options.get("borderStyle", "single")
    margin = options["margin"]
    title = options.get("title")
    title_alignment = options.get("titleAlignment", "left")
    float_option = options.get("float", "left")

    chars = get_border_chars(border_style)
    columns = terminal_columns()
    border_width = get_border_width(border_style)
    margin_left = " " * margin["left"]

    if float_option == "center":
        margin_width = max((columns - content_width - border_width) // 2, 0)
        margin_left = " " * margin_width
    elif float_option == "right":
        margin_width = max(columns - content_width - margin["right"] - border_width, 0)
        margin_left = " " * margin_width

    result = []

    if margin.get("top", 0) > 0:
        result.extend([""] * margin["top"])

    if border_style != "none" or title:
        top_line = chars["topLeft"]
        if title:
            horizontal = chars["top"] * content_width
            title_line = make_title(title, horizontal, title_alignment)
        else:
            title_line = chars["top"] * content_width
        top_line += title_line + chars["topRight"]
        if border_color:
            top_line = apply_color(top_line, border_color)
        if dim_border:
            top_line = dim_text(top_line)
        result.append(margin_left + top_line)

    for line in content.split("\n"):
        left_border = chars["left"]
        right_border = chars["right"]
        if border_color:
            left_border = apply_color(left_border, border_color)
            right_border = apply_color(right_border, border_color)
        if dim_border:
            left_border = dim_text(left_border)
            right_border = dim_text(right_border)
        content_line = line
        if bg_color:
            content_line = apply_bg_color(content_line, bg_color)
        result.append(margin_left + left_border + content_line + right_border)

    if border_style != "none":
        bottom_line = (
            chars["bottomLeft"] + chars["bottom"] * content_width + chars["bottomRight"]
        )
        if border_color:
            bottom_line = apply_color(bottom_line, border_color)
        if dim_border:
            bottom_line = dim_text(bottom_line)
        result.append(margin_left + bottom_line)

    if margin.get("bottom", 0) > 0:
        result.extend([""] * margin["bottom"])

    return "\n".join(result)


def boxen(text, options=None):
    if options is None:
        options = {}
    default_options = {
        "padding": 0,
        "borderStyle": "single",
        "dimBorder": False,
        "textAlignment": "left",
        "float": "left",
        "titleAlignment": "left",
    }
    options = {**default_options, **options}
    if "align" in options:
        options["textAlignment"] = options.pop("align")
    if "borderColor" in options and not is_color_valid(options["borderColor"]):
        raise ValueError(f"Invalid border color: {options['borderColor']}")
    if "backgroundColor" in options and not is_color_valid(options["backgroundColor"]):
        raise ValueError(f"Invalid background color: {options['backgroundColor']}")
    options["padding"] = get_object(options.get("padding", 0))
    options["margin"] = get_object(options.get("margin", 0))
    options = determine_dimensions(text, options)
    processed_text = make_content_text(text, options)
    return box_content(processed_text, options["width"], options)
