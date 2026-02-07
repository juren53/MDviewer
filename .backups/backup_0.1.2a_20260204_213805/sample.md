# Sample Markdown Document

This is a test markdown file to demonstrate the features of **MDviewer**.

## Header Levels

### H3 Header

#### H4 Header

##### H5 Header

###### H6 Header

## Text Formatting

This text demonstrates **bold** and *italic* formatting. You can also use ***bold italic*** together.

## Code Examples

Inline code looks like this: `print("Hello, World!")`

### Python Code Block

```python
def fibonacci(n):
    """Return the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### JavaScript Example

```javascript
function greetUser(name) {
    const message = `Hello, ${name}!`;
    console.log(message);
    return message;
}

// Call the function
greetUser("World");
```

## Lists

### Unordered List

- First item
- Second item
  - Nested item 1
  - Nested item 2
- Third item

### Ordered List

1. First step
2. Second step
3. Third step
   1. Sub-step 1
   2. Sub-step 2

## Tables

| Feature | Status | Priority |
|---------|--------|----------|
| GitHub-style rendering | ✅ Done | High |
| Syntax highlighting | ✅ Done | High |
| Recent files | ✅ Done | Medium |
| Export options | ❌ TODO | Low |

## Blockquotes

> This is a blockquote.
> 
> It can span multiple lines and contain **formatting**.
> 
> > This is a nested blockquote.

## Links

Visit the [GitHub repository](https://github.com) for more information.

## Horizontal Rules

---

## Escaping Characters

Here's how to escape special characters:

\* This is not bold
\_ This is not italic
\` This is not code

## Task Lists (Extended Feature)

- [x] Completed task
- [ ] Pending task
- [ ] Another pending task

## Mathematical Expressions (if supported)

Inline math: $E = mc^2$

Block math:
$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$

---

*This document demonstrates the markdown capabilities of MDviewer.*