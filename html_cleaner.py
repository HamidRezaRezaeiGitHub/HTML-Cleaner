#!/usr/bin/env python3
"""
HTML Cleaner Script

This script purifies HTML content for data extraction by removing:
- All style-related tags (style, link[rel="stylesheet"])
- All style attributes from HTML elements
- All script-related tags
- All media tags (img, video, audio, source, track, embed, object, iframe, svg, canvas)
- All form elements (form, input, button, textarea, select, option, label)
- All navigation elements (nav, header, footer)
- All metadata tags (meta, base, noscript)
- All hidden elements and unnecessary attributes
- Link tags (anchor text is preserved)

The script preserves semantic HTML structure and data content.
"""

from html.parser import HTMLParser
import sys
import html


class HTMLCleaner(HTMLParser):
    """HTML Parser that removes unwanted tags and attributes."""
    
    # Media tags that are self-closing
    SELF_CLOSING_MEDIA_TAGS = {'img', 'source', 'track', 'embed'}
    
    # Media tags that typically have content (not self-closing)
    MEDIA_TAGS_WITH_CONTENT = {'video', 'audio', 'iframe', 'object', 'svg', 'canvas'}
    
    # Media tags to remove (both self-closing and with content)
    MEDIA_TAGS = SELF_CLOSING_MEDIA_TAGS | MEDIA_TAGS_WITH_CONTENT
    
    # Tags that should be removed along with their content
    REMOVE_WITH_CONTENT = {'style', 'script', 'noscript'}
    
    # Form elements to remove with content
    FORM_TAGS = {'form', 'input', 'button', 'textarea', 'select', 'option', 'label', 'fieldset', 'legend', 'datalist', 'output', 'optgroup'}
    
    # Navigation and structural elements to remove with content
    NAV_TAGS = {'nav', 'header', 'footer'}
    
    # Metadata tags to remove (self-closing or with content)
    METADATA_TAGS = {'meta', 'base', 'link'}
    
    # Tags to unwrap (remove tag but keep inner content)
    UNWRAP_TAGS = {'a', 'span'}
    
    def __init__(self):
        super().__init__()
        self.output = []
        self.skip_content = False
        self.current_skip_tag = None
        self.skip_media_content = False
        self.current_media_tag = None
        self.skip_form_content = False
        self.current_form_tag = None
        self.skip_nav_content = False
        self.current_nav_tag = None
        self.in_head = False
        self.in_title = False
    
    def _is_stylesheet_link(self, tag, attrs):
        """Check if a link tag is a stylesheet link."""
        if tag == 'link':
            for attr, value in attrs:
                if attr == 'rel' and value == 'stylesheet':
                    return True
        return False
    
    def _has_hidden_attribute(self, attrs):
        """Check if element has hidden attributes."""
        for attr, value in attrs:
            if attr == 'hidden':
                return True
            if attr == 'aria-hidden' and value == 'true':
                return True
            if attr == 'type' and value == 'hidden':
                return True
        return False
    
    def _clean_attributes(self, attrs):
        """Clean attributes by removing style, href, and noisy attributes."""
        cleaned_attrs = []
        for attr, value in attrs:
            # Remove style attributes
            if attr == 'style':
                continue
            # Remove href attributes
            if attr == 'href':
                continue
            # Remove class and id attributes (optional - can be kept if needed for semantic meaning)
            if attr in ('class', 'id'):
                continue
            # Remove event handler attributes (onclick, onload, etc.)
            if attr.startswith('on'):
                continue
            # Remove data attributes (data-*)
            if attr.startswith('data-'):
                continue
            # Remove aria attributes (accessibility, not needed for data extraction)
            if attr.startswith('aria-'):
                continue
            # Keep all other attributes
            cleaned_attrs.append((attr, value))
        return cleaned_attrs
    
    def _build_tag_string(self, tag, attrs, self_closing=False):
        """Build an HTML tag string with properly escaped attributes."""
        if attrs:
            attrs_str = ' '.join(
                f'{attr}="{html.escape("" if value is None else str(value), quote=True)}"'
                for attr, value in attrs
            )
            if self_closing:
                return f'<{tag} {attrs_str}/>'
            else:
                return f'<{tag} {attrs_str}>'
        else:
            if self_closing:
                return f'<{tag}/>'
            else:
                return f'<{tag}>'
    
    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        # Track if we're in the head section
        if tag == 'head':
            self.in_head = True
        
        # Track if we're in title (we want to keep title content)
        if tag == 'title':
            self.in_title = True
        
        # Skip script, style, and noscript tags completely
        if tag in self.REMOVE_WITH_CONTENT:
            self.skip_content = True
            self.current_skip_tag = tag
            return
        
        # Skip form elements completely
        if tag in self.FORM_TAGS:
            self.skip_form_content = True
            self.current_form_tag = tag
            return
        
        # Skip navigation elements completely
        if tag in self.NAV_TAGS:
            self.skip_nav_content = True
            self.current_nav_tag = tag
            return
        
        # Skip media tags - if they have content, track to skip it
        if tag in self.MEDIA_TAGS:
            if tag in self.MEDIA_TAGS_WITH_CONTENT:
                self.skip_media_content = True
                self.current_media_tag = tag
            return
        
        # Skip metadata tags (except title which we handle above)
        if tag in self.METADATA_TAGS:
            return
        
        # Skip link tags with rel="stylesheet"
        if self._is_stylesheet_link(tag, attrs):
            return
        
        # Skip elements with hidden attributes
        if self._has_hidden_attribute(attrs):
            return
        
        # Unwrap anchor tags (keep content but remove the tag itself)
        if tag in self.UNWRAP_TAGS:
            return
        
        # Clean attributes and build the tag
        cleaned_attrs = self._clean_attributes(attrs)
        self.output.append(self._build_tag_string(tag, cleaned_attrs))
    
    def handle_endtag(self, tag):
        """Handle closing tags."""
        # Track leaving head section
        if tag == 'head':
            self.in_head = False
        
        # Track leaving title
        if tag == 'title':
            self.in_title = False
        
        # Stop skipping content after closing tag
        if self.skip_content and tag == self.current_skip_tag:
            self.skip_content = False
            self.current_skip_tag = None
            return
        
        # Stop skipping form content after closing tag
        if self.skip_form_content and tag == self.current_form_tag:
            self.skip_form_content = False
            self.current_form_tag = None
            return
        
        # Stop skipping navigation content after closing tag
        if self.skip_nav_content and tag == self.current_nav_tag:
            self.skip_nav_content = False
            self.current_nav_tag = None
            return
        
        # Stop skipping media content after closing tag
        if self.skip_media_content and tag == self.current_media_tag:
            self.skip_media_content = False
            self.current_media_tag = None
            return
        
        # Skip end tags for removed tags
        if tag in self.REMOVE_WITH_CONTENT or tag in self.MEDIA_TAGS or tag in self.FORM_TAGS or tag in self.NAV_TAGS or tag in self.METADATA_TAGS:
            return
        
        # Skip end tags for unwrapped tags
        if tag in self.UNWRAP_TAGS:
            return
        
        self.output.append(f'</{tag}>')
    
    def handle_data(self, data):
        """Handle text content."""
        # Skip content if we're in any skip mode
        if self.skip_content or self.skip_media_content or self.skip_form_content or self.skip_nav_content:
            return
        
        # Skip data in head section (except title)
        if self.in_head and not self.in_title:
            return
        
        self.output.append(data)
    
    def handle_comment(self, data):
        """Handle HTML comments - remove all comments to reduce noise."""
        # Comments are noise for data extraction, skip them all
        return
    
    def handle_decl(self, decl):
        """Handle DOCTYPE declarations."""
        self.output.append(f'<!{decl}>')
    
    def handle_startendtag(self, tag, attrs):
        """Handle self-closing tags."""
        # Skip media tags
        if tag in self.MEDIA_TAGS:
            return
        
        # Skip form elements
        if tag in self.FORM_TAGS:
            return
        
        # Skip metadata tags
        if tag in self.METADATA_TAGS:
            return
        
        # Skip link tags with rel="stylesheet"
        if self._is_stylesheet_link(tag, attrs):
            return
        
        # Skip elements with hidden attributes
        if self._has_hidden_attribute(attrs):
            return
        
        # Clean attributes and build the self-closing tag
        cleaned_attrs = self._clean_attributes(attrs)
        self.output.append(self._build_tag_string(tag, cleaned_attrs, self_closing=True))
    
    def get_output(self):
        """Return the cleaned HTML."""
        return ''.join(self.output)


def remove_empty_tags(html_content):
    """
    Remove empty HTML tags recursively until no more can be removed.
    
    Args:
        html_content (str): HTML content to clean
        
    Returns:
        str: HTML content with empty tags removed
    """
    import re
    
    # Tags that should be removed if empty
    # Keep structural tags like html, head, body even if empty
    removable_tags = ['div', 'span', 'p', 'li', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                     'section', 'article', 'aside', 'main', 'figure', 'figcaption',
                     'strong', 'em', 'b', 'i', 'u', 'small', 'mark', 'del', 'ins',
                     'sub', 'sup', 'blockquote', 'pre', 'code', 'kbd', 'samp', 'var',
                     'abbr', 'address', 'cite', 'dfn', 'time', 'dd', 'dt', 'dl']
    
    # Keep running until no more changes
    max_iterations = 50  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        original = html_content
        
        # Remove tags that are completely empty: <tag></tag> or <tag> </tag> or <tag>\n</tag>
        for tag in removable_tags:
            # Match opening tag, optional whitespace, closing tag
            pattern = rf'<{tag}[^>]*>\s*</{tag}>'
            html_content = re.sub(pattern, '', html_content)
        
        # Remove orphaned closing tags more simply
        # Just remove any remaining closing tags that are surrounded by whitespace/newlines
        # This is a simpler approach that catches most orphaned tags
        pattern = r'^\s*</[^>]+>\s*$'
        html_content = re.sub(pattern, '', html_content, flags=re.MULTILINE)
        
        # If nothing changed, we're done
        if html_content == original:
            break
        
        iteration += 1
    
    return html_content


def clean_html(input_file, output_file):
    """
    Clean HTML from input file and write to output file.
    
    Args:
        input_file (str): Path to input HTML file
        output_file (str): Path to output HTML file
    """
    try:
        # Read input HTML
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Clean the HTML
        cleaner = HTMLCleaner()
        cleaner.feed(html_content)
        cleaned_html = cleaner.get_output()
        
        # Post-processing: Remove empty tags
        cleaned_html = remove_empty_tags(cleaned_html)
        
        # Remove blank lines
        lines = cleaned_html.splitlines()
        non_blank_lines = [line for line in lines if line.strip()]
        cleaned_html = '\n'.join(non_blank_lines)
        
        # Consolidate multiple spaces into single space (preserve line structure)
        import re
        cleaned_html = re.sub(r' +', ' ', cleaned_html)
        
        # Add basic formatting: put each tag on its own line for readability
        # This makes it easier for AI to parse while keeping it clean
        cleaned_html = re.sub(r'>([^<\n])', r'>\n\1', cleaned_html)  # Newline after > if text follows
        cleaned_html = re.sub(r'([^>\n])<', r'\1\n<', cleaned_html)  # Newline before < if text precedes
        
        # Remove any resulting blank lines again
        lines = cleaned_html.splitlines()
        non_blank_lines = [line for line in lines if line.strip()]
        cleaned_html = '\n'.join(non_blank_lines)
        
        # Write output HTML
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_html)
        
        print(f"Successfully cleaned HTML from '{input_file}' to '{output_file}'")
        return True
    
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: File not found - {e}\n")
        return False
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return False


if __name__ == "__main__":
    # Default input and output files
    input_file = "input.html"
    output_file = "output.html"
    
    # Allow command-line arguments to override defaults
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    
    # Clean the HTML
    success = clean_html(input_file, output_file)
    sys.exit(0 if success else 1)
