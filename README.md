# Installation

```bash
pip install -r requirements.txt
```

#### Initialize a new project with Cocowizard

```bash
cocowizard init com.company.packagename git@github.com:cocos2d/cocos2d-x.git develop
```

#### Configure project

```bash
cd packagename/projects/packagename
vim cocowizard.yaml

cocowizard update
```

Now you're ready to start opening the generated projects and start working. Whenever you want to add a library or update the project, you can execute 'cocowizard update' and all project files will be updated.
