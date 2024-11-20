## VSCode Configuration

To ensure consistency in the development environment, we recommend the following settings in VSCode:

1. **Install necessary extensions**:
   - Python
   - Black Formatter

2. **Configure VSCode settings**:
   - Open VSCode settings.
   - Add the following settings to your `settings.json` file:
     ```json
     {
         "python.formatting.provider": "black",
         "editor.formatOnSave": true,
         "python.linting.pylintEnabled": true,
         "python.linting.pylintArgs": [
             "--rcfile=\${workspaceFolder}/.pylintrc"
         ]
     }
     ```
