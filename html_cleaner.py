#!/usr/bin/env python3
"""
HTML Cleaner Script

This script purifies HTML content by removing:
- All style-related tags (style, link[rel="stylesheet"])
- All style attributes from HTML elements
- All script-related tags
- All href attributes from links
- All media tags (img, video, audio, source, track, embed, object, iframe)

The script preserves the HTML structure and data content.
"""

from html.parser import HTMLParser
from html.entities import name2codepoint
import sys


class HTMLCleaner(HTMLParser):
    """HTML Parser that removes unwanted tags and attributes."""
    
    # Tags to completely remove (including their content)
    REMOVE_TAGS = {'style', 'script'}
    
    # Media tags to remove
    MEDIA_TAGS = {'img', 'video', 'audio', 'source', 'track', 'embed', 'object', 'iframe'}
    
    # Tags that should be removed along with their content
    REMOVE_WITH_CONTENT = {'style', 'script'}
    
    def __init__(self):
        super().__init__()
        self.output = []
        self.skip_content = False
        self.current_skip_tag = None
        self.skip_media_content = False
        self.current_media_tag = None
    
    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        # Skip script and style tags completely
        if tag in self.REMOVE_WITH_CONTENT:
            self.skip_content = True
            self.current_skip_tag = tag
            return
        
        # Skip media tags and their content
        if tag in self.MEDIA_TAGS:
            self.skip_media_content = True
            self.current_media_tag = tag
            return
        
        # Skip link tags with rel="stylesheet"
        if tag == 'link':
            for attr, value in attrs:
                if attr == 'rel' and value == 'stylesheet':
                    return
        
        # Clean attributes
        cleaned_attrs = []
        for attr, value in attrs:
            # Remove style attributes
            if attr == 'style':
                continue
            # Remove href attributes
            if attr == 'href':
                continue
            # Keep all other attributes
            cleaned_attrs.append((attr, value))
        
        # Build the tag
        if cleaned_attrs:
            attrs_str = ' '.join(f'{attr}="{value}"' for attr, value in cleaned_attrs)
            self.output.append(f'<{tag} {attrs_str}>')
        else:
            self.output.append(f'<{tag}>')
    
    def handle_endtag(self, tag):
        """Handle closing tags."""
        # Stop skipping content after closing tag
        if self.skip_content and tag == self.current_skip_tag:
            self.skip_content = False
            self.current_skip_tag = None
            return
        
        # Stop skipping media content after closing tag
        if self.skip_media_content and tag == self.current_media_tag:
            self.skip_media_content = False
            self.current_media_tag = None
            return
        
        # Skip end tags for removed tags
        if tag in self.REMOVE_WITH_CONTENT or tag in self.MEDIA_TAGS:
            return
        
        # Skip link tags
        if tag == 'link':
            return
        
        self.output.append(f'</{tag}>')
    
    def handle_data(self, data):
        """Handle text content."""
        if not self.skip_content and not self.skip_media_content:
            self.output.append(data)
    
    def handle_comment(self, data):
        """Handle HTML comments."""
        if not self.skip_content:
            self.output.append(f'<!--{data}-->')
    
    def handle_decl(self, decl):
        """Handle DOCTYPE declarations."""
        self.output.append(f'<!{decl}>')
    
    def handle_startendtag(self, tag, attrs):
        """Handle self-closing tags."""
        # Skip media tags
        if tag in self.MEDIA_TAGS:
            return
        
        # Skip link tags with rel="stylesheet"
        if tag == 'link':
            for attr, value in attrs:
                if attr == 'rel' and value == 'stylesheet':
                    return
        
        # Clean attributes
        cleaned_attrs = []
        for attr, value in attrs:
            # Remove style attributes
            if attr == 'style':
                continue
            # Remove href attributes
            if attr == 'href':
                continue
            # Keep all other attributes
            cleaned_attrs.append((attr, value))
        
        # Build the self-closing tag
        if cleaned_attrs:
            attrs_str = ' '.join(f'{attr}="{value}"' for attr, value in cleaned_attrs)
            self.output.append(f'<{tag} {attrs_str} />')
        else:
            self.output.append(f'<{tag} />')
    
    def get_output(self):
        """Return the cleaned HTML."""
        return ''.join(self.output)


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
        
        # Write output HTML
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_html)
        
        print(f"Successfully cleaned HTML from '{input_file}' to '{output_file}'")
        return True
    
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
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
