# PROMPT RULES

- Always explain your approach to carrying out a task, outline these tasks, and don't modify or add code until I approve it.
- After each task, append the prompts I type and a brief explanation of the tasks carried out in the @PROMPTS.md file. Then add the tasks and changes to the @TASKS_AND_CHANGES.md app.

# PROGRAMMING RULES

### Python Rules

- Follow PEP 8 - Use consistent indentation (4 spaces), line length (less than or equal to 79 characters) and naming conventions
- Use meaningful variable and function names
- Keep functions small and focused
- Write docstrings
- Use list comprehensions and generators wisely
- Leverage built-in functions and libraries
- Avoid mutable default arguments. Use None and check inside the function
- Use virtual environments. Keep dependencies isolated.
- Handle exceptions explicitly. Don't use except: without specifying the error
- Use context managers (with) for files, DB connections, etc.
- Follow OOP or functional style consistently. Don't mix patterns randomly
- Test python code using unittest or pytest
- Write type hints.
- Keep modules cohesive. Each module should focus on a single responsibility.
- Refactor regularly. Don't let code rot; keep it clean and maintainable.

### HTML Rules

- Use semantic tags.
- Keep markup clean and minimal. Don't add unnecessary wrappers or redundant tags.
- Use meaningful alt text for images.
- Structure content heirarchically with headings, maintaining a logical order.
- Keep forms accessible.
- Avoid inline styles and scripts.
- Use descriptive titles and metadata.
- Use tables only for tabular data.
- Use ARIA attributes responsibly, only when native HTML doesn't suffice.
- Ensure mobile responsiveness.
- Indent consistently.

### JS Rules

- Use const and let over var.
- Use strict equality to avoid type coercion issues.
- Keep functions small and modular for easy testing and maintenance.
- Prefer arrow functions for callbacks, cleaner syntax and lexical this.
- Avoid polluting the global scope, use modules or IIFES.
- Use descriptive variable/function names.
- Handle errors properly. Alwyas use try/catch or .catch() for promises
- Use async/await instead of raw promises.
- Avoid callback hell. Refactor with promises or async/await.
- Lint code using ESLint or Prettier to enforce consistency.
- Keep DOM manipulation minimal. Cache selector, batch updates, use frameworks when needed.
- Write pure function when possible. Functions should not modify external state unexpectedly.
- Use object/array destructuring as a clean way to extract data.
- Avoid deeply nested code. Refactor with early returns or helper functions.
- Test code. Use Jest, Mocha and other similar testing libraries.

### CSS Rules

- Keep selectors short and meaningful. Avoid overly specific selectors like #main .container ul li span.
- Use classes over IDs for styling. 
- Follow a naming convention like BEM
- Group related styles logically to improve readability.
- Avoid inline styles.
- Use CSS variables to make theme changes easy.
- Keep CSS DRY. Extract common tyles into reusable classes.
- Use responsive design techniques like media queries, fluid layouts, flexbox, grid.
- Avoid !important, except as a last resort.
- Organize files modularly. Split large CSS into multiple smaller files.
- Minimize nesting if using preprocessors.
- Optimize for performance. Don't use heavy selectors like div > *.
- Use reset or normalize.css to ensure consistent cross-browser styls.
- Keep accessibility in mind. Proper contrast, focus states, readable fonts.

### Flask Projects 
- As best as possible try to avoid adding CSS and JS code in the html templates and put them in seperate files in the static folder and import them within html files