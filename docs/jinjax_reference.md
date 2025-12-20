Guides

Introduction
============

JinjaX is a Python library for creating reusable "components" - encapsulated template snippets that can take arguments and render to HTML. They are similar to React or Vue components, but they render on the server side, not in the browser.

Unlike Jinja's `{% include "..." %}` or macros, JinjaX components integrate naturally with the rest of your template code.

```
<div>
  <Card class="bg-gray">
    <h1>Products</h1>
    {% for product in products %}
      <Product product={{ product }} />
    {% endfor %}
  </Card>
</div>

```

Features [¶](https://jinjax.scaletti.dev/guides/#s-features)
------------------------------------------------------------

### Simple [¶](https://jinjax.scaletti.dev/guides/#s-simple)

JinjaX components are simple Jinja templates. You use them as if they were HTML tags without needing to import them: they're easy to use and easy to read.

### Encapsulated [¶](https://jinjax.scaletti.dev/guides/#s-encapsulated)

They are independent of each other and can link to their own CSS and JS, so you can freely copy and paste components between applications.

### Testable [¶](https://jinjax.scaletti.dev/guides/#s-testable)

All components can be unit tested independently of the pages where they are used.

### Composable [¶](https://jinjax.scaletti.dev/guides/#s-composable)

A JinjaX component can wrap HTML code or other components with a natural syntax, treating them as if they were native HTML tags.

### Modern [¶](https://jinjax.scaletti.dev/guides/#s-modern)

They are a great complement to technologies like [TailwindCSS](https://tailwindcss.com/), [htmx](https://htmx.org/), or [Hotwire](https://hotwired.dev/).

Usage [¶](https://jinjax.scaletti.dev/guides/#s-usage)
------------------------------------------------------

#### Install [¶](https://jinjax.scaletti.dev/guides/#s-install)

Install the library using `pip`.

```
pip install jinjax

```

#### Components folder [¶](https://jinjax.scaletti.dev/guides/#s-components-folder)

Then, create a folder that will contain your components, for example:

```
└ myapp/
    ├── app.py
    ├── components/             🆕
    │   └── Card.jinja          🆕
    ├── static/
    ├── templates/
    └── views/
└─ requirements.txt

```

#### Catalog [¶](https://jinjax.scaletti.dev/guides/#s-catalog)

Finally, you must create a "catalog" of components in your app. This object manages the components and their global settings. You then add the path to your components folder to this catalog:

```
from jinjax import Catalog

catalog = Catalog()
catalog.add_folder("myapp/components")

```

#### Render [¶](https://jinjax.scaletti.dev/guides/#s-render)

You'll use the catalog to render components from your views.

```
def myview():
  ...
  return catalog.render(
    "Page",
    title="Lorem ipsum",
    message="Hello",
  )

```

In this example, we're rendering a component for the whole page, but you can also render smaller components, even from inside a regular Jinja template by adding the catalog as a global:

```
app.jinja_env.globals["catalog"] = catalog

```

```
{% block content %}
<div>
  {{ catalog.irender("LikeButton", title="Like and subscribe!", post=post) }}
</div>
<p>Lorem ipsum</p>
{{ catalog.irender("CommentForm", post=post) }}
{% endblock %}

```

How It Works [¶](https://jinjax.scaletti.dev/guides/#s-how-it-works)
--------------------------------------------------------------------

JinjaX uses Jinja to render component templates. It works as a pre-processor, replacing code like:

```
<Component attr="value">content</Component>

```

with function calls like:

```
{% call catalog.irender("Component", attr="value") %}content{% endcall %}

```

These calls are evaluated at render time. Each call loads the component file's source, extracts the names of CSS/JS files and required/optional attributes, pre-processes the template (replacing components with function calls as described above), and finally renders the complete template.

### Reusing Jinja's Globals, Filters, and Tests [¶](https://jinjax.scaletti.dev/guides/#s-reusing-jinjas-globals-filters-and-tests)

You can add your own global variables and functions, filters, tests, and Jinja extensions when creating the catalog:

```
from jinjax import Catalog

catalog = Catalog(
    globals={ ... },
    filters={ ... },
    tests={ ... },
    extensions=[ ... ],
)

```

or afterward.

```
catalog.jinja_env.globals.update({ ... })
catalog.jinja_env.filters.update({ ... })
catalog.jinja_env.tests.update({ ... })
catalog.jinja_env.extensions.extend([ ... ])

```

The ["do" extension](https://jinja.palletsprojects.com/en/3.0.x/extensions/#expression-statement) is enabled by default, so you can write things like:

```
{% do attrs.set(class="btn", disabled=True) %}

```

### Reusing an Existing Jinja Environment [¶](https://jinjax.scaletti.dev/guides/#s-reusing-an-existing-jinja-environment)

You can also reuse an existing Jinja Environment, for example:

#### Flask: [¶](https://jinjax.scaletti.dev/guides/#s-flask)

```
app = Flask(__name__)

# Here we add the Flask Jinja globals, filters, etc., like `url_for()`
catalog = jinjax.Catalog(jinja_env=app.jinja_env)

```

#### Django: [¶](https://jinjax.scaletti.dev/guides/#s-django)

First, configure Jinja in `settings.py` and [jinja_env.py](https://docs.djangoproject.com/en/5.0/topics/templates/#django.template.backends.jinja2.Jinja2).

To have a separate "components" folder for shared components and also have "components" subfolders at each Django app level:

```
import jinjax
from jinja2.loaders import FileSystemLoader

def environment(loader: FileSystemLoader, **options):
    env = Environment(loader=loader, **options)

    ...

    env.add_extension(jinjax.JinjaX)
    catalog = jinjax.Catalog(jinja_env=env)

    catalog.add_folder("components")
    for dir in loader.searchpath:
        catalog.add_folder(os.path.join(dir, "components"))

    return env

```

#### FastAPI: [¶](https://jinjax.scaletti.dev/guides/#s-fastapi)

```
import jinjax
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

templates.env.add_extension(jinjax.JinjaX)
catalog = jinjax.Catalog(jinja_env=templates.env)
catalog.add_folder("templates/components")

@app.get("/")
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

Guides

Introduction
============

JinjaX is a Python library for creating reusable "components" - encapsulated template snippets that can take arguments and render to HTML. They are similar to React or Vue components, but they render on the server side, not in the browser.

Unlike Jinja's `{% include "..." %}` or macros, JinjaX components integrate naturally with the rest of your template code.

```
<div>
  <Card class="bg-gray">
    <h1>Products</h1>
    {% for product in products %}
      <Product product={{ product }} />
    {% endfor %}
  </Card>
</div>

```

Features [¶](https://jinjax.scaletti.dev/guides/#s-features)
------------------------------------------------------------

### Simple [¶](https://jinjax.scaletti.dev/guides/#s-simple)

JinjaX components are simple Jinja templates. You use them as if they were HTML tags without needing to import them: they're easy to use and easy to read.

### Encapsulated [¶](https://jinjax.scaletti.dev/guides/#s-encapsulated)

They are independent of each other and can link to their own CSS and JS, so you can freely copy and paste components between applications.

### Testable [¶](https://jinjax.scaletti.dev/guides/#s-testable)

All components can be unit tested independently of the pages where they are used.

### Composable [¶](https://jinjax.scaletti.dev/guides/#s-composable)

A JinjaX component can wrap HTML code or other components with a natural syntax, treating them as if they were native HTML tags.

### Modern [¶](https://jinjax.scaletti.dev/guides/#s-modern)

They are a great complement to technologies like [TailwindCSS](https://tailwindcss.com/), [htmx](https://htmx.org/), or [Hotwire](https://hotwired.dev/).

Usage [¶](https://jinjax.scaletti.dev/guides/#s-usage)
------------------------------------------------------

#### Install [¶](https://jinjax.scaletti.dev/guides/#s-install)

Install the library using `pip`.

```
pip install jinjax

```

#### Components folder [¶](https://jinjax.scaletti.dev/guides/#s-components-folder)

Then, create a folder that will contain your components, for example:

```
└ myapp/
    ├── app.py
    ├── components/             🆕
    │   └── Card.jinja          🆕
    ├── static/
    ├── templates/
    └── views/
└─ requirements.txt

```

#### Catalog [¶](https://jinjax.scaletti.dev/guides/#s-catalog)

Finally, you must create a "catalog" of components in your app. This object manages the components and their global settings. You then add the path to your components folder to this catalog:

```
from jinjax import Catalog

catalog = Catalog()
catalog.add_folder("myapp/components")

```

#### Render [¶](https://jinjax.scaletti.dev/guides/#s-render)

You'll use the catalog to render components from your views.

```
def myview():
  ...
  return catalog.render(
    "Page",
    title="Lorem ipsum",
    message="Hello",
  )

```

In this example, we're rendering a component for the whole page, but you can also render smaller components, even from inside a regular Jinja template by adding the catalog as a global:

```
app.jinja_env.globals["catalog"] = catalog

```

```
{% block content %}
<div>
  {{ catalog.irender("LikeButton", title="Like and subscribe!", post=post) }}
</div>
<p>Lorem ipsum</p>
{{ catalog.irender("CommentForm", post=post) }}
{% endblock %}

```

How It Works [¶](https://jinjax.scaletti.dev/guides/#s-how-it-works)
--------------------------------------------------------------------

JinjaX uses Jinja to render component templates. It works as a pre-processor, replacing code like:

```
<Component attr="value">content</Component>

```

with function calls like:

```
{% call catalog.irender("Component", attr="value") %}content{% endcall %}

```

These calls are evaluated at render time. Each call loads the component file's source, extracts the names of CSS/JS files and required/optional attributes, pre-processes the template (replacing components with function calls as described above), and finally renders the complete template.

### Reusing Jinja's Globals, Filters, and Tests [¶](https://jinjax.scaletti.dev/guides/#s-reusing-jinjas-globals-filters-and-tests)

You can add your own global variables and functions, filters, tests, and Jinja extensions when creating the catalog:

```
from jinjax import Catalog

catalog = Catalog(
    globals={ ... },
    filters={ ... },
    tests={ ... },
    extensions=[ ... ],
)

```

or afterward.

```
catalog.jinja_env.globals.update({ ... })
catalog.jinja_env.filters.update({ ... })
catalog.jinja_env.tests.update({ ... })
catalog.jinja_env.extensions.extend([ ... ])

```

The ["do" extension](https://jinja.palletsprojects.com/en/3.0.x/extensions/#expression-statement) is enabled by default, so you can write things like:

```
{% do attrs.set(class="btn", disabled=True) %}

```

### Reusing an Existing Jinja Environment [¶](https://jinjax.scaletti.dev/guides/#s-reusing-an-existing-jinja-environment)

You can also reuse an existing Jinja Environment, for example:

#### Flask: [¶](https://jinjax.scaletti.dev/guides/#s-flask)

```
app = Flask(__name__)

# Here we add the Flask Jinja globals, filters, etc., like `url_for()`
catalog = jinjax.Catalog(jinja_env=app.jinja_env)

```

#### Django: [¶](https://jinjax.scaletti.dev/guides/#s-django)

First, configure Jinja in `settings.py` and [jinja_env.py](https://docs.djangoproject.com/en/5.0/topics/templates/#django.template.backends.jinja2.Jinja2).

To have a separate "components" folder for shared components and also have "components" subfolders at each Django app level:

```
import jinjax
from jinja2.loaders import FileSystemLoader

def environment(loader: FileSystemLoader, **options):
    env = Environment(loader=loader, **options)

    ...

    env.add_extension(jinjax.JinjaX)
    catalog = jinjax.Catalog(jinja_env=env)

    catalog.add_folder("components")
    for dir in loader.searchpath:
        catalog.add_folder(os.path.join(dir, "components"))

    return env

```

#### FastAPI: [¶](https://jinjax.scaletti.dev/guides/#s-fastapi)

```
import jinjax
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

templates.env.add_extension(jinjax.JinjaX)
catalog = jinjax.Catalog(jinja_env=templates.env)
catalog.add_folder("templates/components")

@app.get("/")
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```Components
==========

Declaring and using components.

Declaring and Using Components [¶](https://jinjax.scaletti.dev/guides/components/#s-declaring-and-using-components)
-------------------------------------------------------------------------------------------------------------------

Components are simple text files that look like regular Jinja templates, with three requirements:

First, components must be placed inside a folder registered in the catalog or a subfolder of it.

```
catalog.add_folder("myapp/components")

```

You can name that folder whatever you want (not just "components"). You can also add more than one folder:

```
catalog.add_folder("myapp/layouts")
catalog.add_folder("myapp/components")

```

If you end up having more than one component with the same name, the one in the first folder will take priority.

Second, they must have a ".jinja" extension. This also helps code editors automatically select the correct language syntax for highlighting. However, you can configure this extension in the catalog.

Third, the filename must be either PascalCased (like Python classes) or "kebab-cased" (lowercase with words separated by dashes).

The PascalCased name of the file (minus the extension) is always how you call the component (even if the filename is kebab-cased). This is how JinjaX differentiates a component from a regular HTML tag when using it.

For example, if the file is "components/PersonForm.jinja":

```
└ myapp/
  ├── app.py
  ├── components/
        └─ PersonForm.jinja

```

The name of the component is "PersonForm" and can be called like this:

From Python code or a non-component template:

-   `catalog.render("PersonForm")`

From another component:

-   `<PersonForm> some content </PersonForm>`, or
-   `<PersonForm />`

If you prefer you can also choose to use kebab-cased filenames:

```
└ myapp/
  ├── app.py
  ├── components/
        └─ person-form.jinja

```

The name of the component will still be "PersonForm" and you will use it in the same way as before.

warning

Do not mix PascalCased files with kebab-cased files. Choose a name format you like and stick with it.

### Subfolders [¶](https://jinjax.scaletti.dev/guides/components/#s-subfolders)

If the component is in a subfolder, the name of that folder becomes part of its name too:

```
└ myapp/
  ├── app.py
  ├── components/
        └─ Person/
            └─ Form.jinja

```

A "components/person/PersonForm.jinja" component is named "Person.Form", meaning the name of the subfolder and the name of the file separated by a dot. This is the full name you use to call it:

From Python code or a non-component template:

-   `catalog.render("Person.Form")`

From another component:

-   `<Person.Form> some content </Person.Form>`, or
-   `<Person.Form />`

You can also use kebab-cased filenames in subfolders and call them the same way:

```
└ myapp/
  ├── app.py
  ├── components/
        └─ password-reset/
            └─ form.jinja

```

From Python code or a non-component template:

-   `catalog.render("PasswordReset.Form")`

From another component:

-   `<PasswordReset.Form> some content </PasswordReset.Form>`, or
-   `<PasswordReset.Form />`

Anatomy of a Component [¶](https://jinjax.scaletti.dev/guides/components/#s-anatomy-of-a-component)
---------------------------------------------------------------------------------------------------

[![](https://jinjax.scaletti.dev/static/img/anatomy-en.svg)](https://jinjax.scaletti.dev/static/img/anatomy-en.svg)

Arguments
=========

More often than not, a component takes one or more arguments to render.

Every argument must be declared at the beginning of the component with `{#def arg1, arg2, ... #}`.

```
{#def action, method="post", multipart=False #}

<form method="{{ method }}" action="{{ action }}"
  {%- if multipart %} enctype="multipart/form-data"{% endif %}
>
  {{ content }}
</form>

```

In this example, the component takes three arguments: "action", "method", and "multipart". The last two have default values, so they are optional, but the first one doesn't. That means it must be passed a value when rendering the component.

The syntax is exactly like how you declare the arguments of a Python function (in fact, it's parsed by the same code), so it can even include type comments, although they are not used by JinjaX (yet!).

```
{#def
  data: dict[str, str],
  method: str = "post",
  multipart: bool = False
#}
...

```

Passing Arguments [¶](https://jinjax.scaletti.dev/guides/arguments/#s-passing-arguments)
----------------------------------------------------------------------------------------

There are two types of arguments: strings and expressions.

### String [¶](https://jinjax.scaletti.dev/guides/arguments/#s-string)

Strings are passed like regular HTML attributes:

```
<Form action="/new" method="PATCH"> ... </Form>

<Alert message="Profile updated" />

<Card title="Hello world" type="big"> ... </Card>

```

### Expressions [¶](https://jinjax.scaletti.dev/guides/arguments/#s-expressions)

There are two different but equivalent ways to pass non-string arguments:

"Jinja-like", where you use double curly braces instead of quotes:

Jinja-like

```
<Example
    columns={{ 2 }}
    tabbed={{ False }}
    panels={{ {'one': 'lorem', 'two': 'ipsum'} }}
    class={{ 'bg-' + color }}
/>

```

... and "Vue-like", where you keep using quotes, but prefix the name of the attribute with a colon:

Vue-like

```
<Example
    :columns="2"
    :tabbed="False"
    :panels="{'one': 'lorem', 'two': 'ipsum'}"
    :class="'bg-' + color"
/>

```

info

For `True` values, you can just use the name, like in HTML:

```
<Example class="green" hidden /> 
```

info

You can also use dashes when passing an argument, but they will be translated to underscores:

```
<Example aria-label="Hi" />

```

Example.jinja

```
{#def aria_label = "" #}
... 
```

With Content [¶](https://jinjax.scaletti.dev/guides/arguments/#s-with-content)
------------------------------------------------------------------------------

There is always an extra implicit argument: the content inside the component. Read more about it in the [next](https://jinjax.scaletti.dev/guide/slots/) section.

Extra Arguments [¶](https://jinjax.scaletti.dev/guides/arguments/#s-extra-arguments)
------------------------------------------------------------------------------------

If you pass arguments not declared in a component, those are not discarded but rather collected in an `attrs` object.

You then call `attrs.render()` to render the received arguments as HTML attributes.

For example, this component:

Card.jinja

```
{#def title #}
<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>

```

Called as:

```
<Card title="Products" class="mb-10" open>bla</Card>

```

Will be rendered as:

```
<div class="mb-10" open>
  <h1>Products</h1>
  bla
</div>

```

You can add or remove arguments before rendering them using the other methods of the `attrs` object. For example:

```
{#def title #}
{% do attrs.set(id="mycard") -%}

<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>

```

Or directly in the `attrs.render()` call:

```
{#def title #}

<div {{ attrs.render(id="mycard") }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>

```

info

The string values passed into components as attrs are not cast to `str` until their string representation is actually needed, for example when `attrs.render()` is invoked.

### `attrs` Methods [¶](https://jinjax.scaletti.dev/guides/arguments/#s-attrs-methods)

#### `.render(name=value, ...)` [¶](https://jinjax.scaletti.dev/guides/arguments/#s-rendernamevalue)

Renders the attributes and properties as a string.

Any arguments you use with this function are merged with the existing attributes/properties by the same rules as the `HTMLAttrs.set()` function:

-   Pass a name and a value to set an attribute (e.g. `type="text"`)
-   Use `True` as a value to set a property (e.g. `disabled`)
-   Use `False` to remove an attribute or property
-   The existing attribute/property is overwritten except if it is `class`. The new classes are appended to the old ones instead of replacing them.
-   The underscores in the names will be translated automatically to dashes, so `aria_selected` becomes the attribute `aria-selected`.

To provide consistent output, the attributes and properties are sorted by name and rendered like this: `<sorted attributes> + <sorted properties>`.

```
<Example class="ipsum" width="42" data-good />

```

```
<div {{ attrs.render() }}>
<!-- <div class="ipsum" width="42" data-good> -->

<div {{ attrs.render(class="abc", data_good=False, tabindex=0) }}>
<!-- <div class="abc ipsum" width="42" tabindex="0"> -->

```

warning

Using `<Component {{ attrs.render() }}>` to pass the extra arguments to other components WILL NOT WORK. That is because the components are translated to macros before the page render.

You must pass them as the special argument `_attrs`.

```
{#--- WRONG 😵 ---#}
<MyButton {{ attrs.render() }} />

{#--- GOOD 👍 ---#}
<MyButton _attrs={{ attrs }} />
<MyButton :_attrs="attrs" /> 
```

#### `.set(name=value, ...)` [¶](https://jinjax.scaletti.dev/guides/arguments/#s-setnamevalue)

Sets an attribute or property

-   Pass a name and a value to set an attribute (e.g. `type="text"`)
-   Use `True` as a value to set a property (e.g. `disabled`)
-   Use `False` to remove an attribute or property
-   If the attribute is "class", the new classes are appended to the old ones (if not repeated) instead of replacing them.
-   The underscores in the names will be translated automatically to dashes, so `aria_selected` becomes the attribute `aria-selected`.

Adding attributes/properties

```
{% do attrs.set(
  id="loremipsum",
  disabled=True,
  data_test="foobar",
  class="m-2 p-4",
) %}

```

Removing attributes/properties

```
{% do attrs.set(
  title=False,
  disabled=False,
  data_test=False,
  class=False,
) %}

```

#### `.setdefault(name=value, ...)` [¶](https://jinjax.scaletti.dev/guides/arguments/#s-setdefaultnamevalue)

Adds an attribute, but only if it's not already present.

The underscores in the names will be translated automatically to dashes, so `aria_selected` becomes the attribute `aria-selected`.

```
{% do attrs.setdefault(
    aria_label="Products"
) %}

```

#### `.add_class(name1, name2, ...)` [¶](https://jinjax.scaletti.dev/guides/arguments/#s-add_classname1-name2)

Adds one or more classes to the list of classes, if not already present.

```
{% do attrs.add_class("hidden") %}
{% do attrs.add_class("active", "animated") %}

```

#### `.remove_class(name1, name2, ...)` [¶](https://jinjax.scaletti.dev/guides/arguments/#s-remove_classname1-name2)

Removes one or more classes from the list of classes.

```
{% do attrs.remove_class("hidden") %}
{% do attrs.remove_class("active", "animated") %}

```

#### `.get(name, default=None)` [¶](https://jinjax.scaletti.dev/guides/arguments/#s-getname-defaultnone)

Returns the value of the attribute or property, or the default value if it doesn't exist.

```
{%- set role = attrs.get("role", "tab") %}
```

Organizing your components
==========================

Keeping Your Components Neat and Tidy

There are two ways to organize your components to your liking: using subfolders and/or adding multiple component folders.

### Using subfolders [¶](https://jinjax.scaletti.dev/guides/organization/#s-using-subfolders)

To call components inside subfolders, you use a dot after each subfolder name. For example, to call a `Button.jinja` component inside a `form` subfolder, you use the name:

```
<form.Button> ... </form.Button>

```

If the component is inside a sub-subfolder, for instance `product/items/Header.jinja`, you use a dot for each subfolder:

```
<product.items.Header> ... </product.items.Header>

```

### Adding multiple separate folders [¶](https://jinjax.scaletti.dev/guides/organization/#s-adding-multiple-separate-folders)

Adding multiple separate folders makes JinjaX search for a component in each folder, in order, until it finds it. This means that even if different folders have components with the same name, the component found first will be used.

For example, imagine that you add these three folders:

```
A/
├── Alert.jinja
└── common
    └── Error.jinja

whatever/B/
├── Alert.jinja
└── form
    └── Error.jinja
└── common
    └── Welcome.jinja

C/
├── Alert.jinja
├── Header.jinja
└── common
    └── Error.jinja
    └── Welcome.jinja

```

```
catalog.add_folder("A")
catalog.add_folder("whatever/B")
catalog.add_folder("C")

```

-   Even though there is an `Alert.jinja` in all three folders, it will be loaded from "A", because that folder was added first.
-   `common.Error` will also be loaded from "A", but `form.Error` will be loaded from "B", because the subfolder is part of the component's name.
-   `common.Welcome` will be loaded from "B" and `Header` from "C", because that's where they will be found first.
-   Finally, using `common.Header` will raise an error, because there is no component under that name.

### Third-party components libraries [¶](https://jinjax.scaletti.dev/guides/organization/#s-third-party-components-libraries)

You can also add a folder of components from an installed library. For example:

```
import jinjax_ui
...
catalog.add_folder(jinjax_ui.components_path)

```

In order for this to work, the path given by the library should be absolute.

### Prefixes [¶](https://jinjax.scaletti.dev/guides/organization/#s-prefixes)

The `add_folder()` method takes an optional `prefix` argument.

The prefix acts like a namespace. For example, the name of a `Card.jinja` component is, by default, "Card", but under the prefix "common", it becomes "common:Card".

The rule for subfolders remains the same: a `wrappers/Card.jinja` name is, by default, "wrappers.Card", but under the prefix "common", it becomes "common:wrappers.Card".

An important caveat is that when a component under a prefix calls another component without a prefix, the called component is searched first under the caller's prefix and then under the empty prefix. This allows third-party component libraries to call their own components without knowing under what prefix your app is using them.

warning

The prefixes take precedence over subfolders, so don't create a subfolder with the same name as a prefix because it will be ignored.

If under the same prefix there is more than one component with the same name in multiple added folders, the one in the folder added first takes precedence. You can use this to override components loaded from a library by simply adding a folder first with the target prefix.

Slots / Content
Working with content in components.

Everything between the open and close tags of a component will be rendered and passed to the component as an implicit content variable.

This is a very common pattern, and it is called a slot. A slot is a placeholder for content that can be provided by the user of the component. For example, we may have a <FancyButton> component that supports usage like this:

<FancyButton>
  <i class="icon"></i> Click me!
</FancyButton>
The template of <FancyButton> looks like this:

<button class="fancy-btn">
  {{ content }}
</button>
slot diagram

The <FancyButton> is responsible for rendering the outer <button> (and its fancy styling), while the inner content is provided by the parent component.

A great use case for the content variable is creating layout components:

ArchivePage.jinja
{#def posts #}
<Layout title="Archive">
  {% for post in posts %}
    <Post :post=post />
  {% endfor %}
</Layout>
Layout.jinja
{#def title #}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
</head>
<body>
  {{ content }}
</body>
Fallback Content ¶
There are cases when it's useful to specify fallback (i.e. default) content for a slot, to be rendered only when no content is provided. For example, in a <SubmitButton> component:

<button type="submit">
  {{ content }}
</button>
We might want the text "Submit" to be rendered inside the <button> if the parent didn't provide any slot content. The special "content" variable is just a string like any other, so we can test if it's empty to make "Submit" the fallback content:

<button type="submit">
  {% if content %}
    {{ content }}
  {% else %}
    Submit  <!-- fallback content -->
  {% endif %}
</button>
Now when we use <SubmitButton> in a parent component, providing no content for the slot:

<SubmitButton />
info
The content of a self-closing component is an empty string.
This will render the fallback content, "Submit":

<button type="submit">Submit</button>
But if we provide content:

<SubmitButton>Save</SubmitButton>
Then the provided content will be rendered instead:

<button type="submit">Save</button>
Multiple content slots (a.k.a. "named slots") ¶
There are cases when a component is complex enough to need multiple content slots. For example, a <Modal> component might need a header, a body, and a footer content.

One way to implement this is by using multiple content slots. To do so, instead of rendering content as a string, you can also call it with a name. Then, the parent component can provide content for that name.

_slot variable

Note the _slot special variable. This is automatically available in the content of the parent component and contains the name that the component has used to request its content.

The _slot variable is scoped to the content of that component, so it's not available outside of it:

<FancyButton>
  {% if _slot == "hi" %} {# <--- _slot #}
  Hello{% endif %}
</FancyButton>

<FancyButton2>
  {% if _slot == "hi" %} {# <--- This _slot is a different one #}
  Sup?{% endif %}
</FancyButton2>

{{ _slot }}   {# <--- Undefined variable #}
Composability: better than named slots ¶
Named slots are a quick way to have multiple content slots, but are a bit messy beyond some simple cases.

Composability offers a more flexible and idiomatic approach when multiple content slots are needed. The idea is to have separated components for each content slot, and then compose them together. Let's explore this concept using the same example as above.

Consider a Modal component that requires three distinct sections: a header, a body, and a footer. Instead of using named slots, we can create separate components for each section and compose them within a Modal component wrapper.

<Modal>

  <ModalHeader>
    <i class="icon-rocket"></i>
    Hello World!
  </ModalHeader>

  <ModalBody>
    <p>The modal body.</p>
  </ModalBody>

  <ModalFooter>
    <button>Cancel</button>
    <button>Save</button>
  </ModalFooter>

</Modal>
Now, the Modal component is responsible for rendering the outer <dialog> and its styling, while the inner content is provided by the child components.

Modal.jinja
<dialog class="modal">
  {{ content }}
</dialog>
ModalHeader.jinja
<header class="modal-header">
  <h2 class="modal-title">
    {{ content }}
  </h2>
  <CloseButton />
</header>
ModalBody.jinja
<div class="modal-body">
  {{ content }}
</div>
ModalFooter.jinja
<footer class="modal-footer">
  {{ content }}
</footer>
Advantages of Composability ¶
Flexibility: You can easily rearrange, omit, or add new sections without modifying the core Modal component.
Reusability: Each section (ModalHeader, ModalBody, ModalFooter) can be used independently or within other components.
Maintainability: It's easier to update or style individual sections without affecting the others.
Testing components with content ¶
To test a component in isolation, you can manually send a content argument using the special _content argument:

catalog.render("PageLayout", title="Hello world", _content="TEST")

Adding CSS and JS assets
========================

Your components might need custom styles or custom JavaScript for many reasons.

Instead of using global stylesheets or script files, writing assets for each individual component has several advantages:

-   Portability: You can copy a component from one project to another, knowing it will keep working as expected.
-   Performance: Only load the CSS and JS that you need on each page. Additionally, the browser will have already cached the assets of the components for other pages that use them.
-   Simple testing: You can test the JS of a component independently from others.

Auto-loading assets [¶](https://jinjax.scaletti.dev/guides/css-and-js/#s-auto-loading-assets)
---------------------------------------------------------------------------------------------

JinjaX searches for `.css` and `.js` files with the same name as your component in the same folder and automatically adds them to the list of assets included on the page. For example, if your component is `components/common/Form.jinja`, both `components/common/Form.css` and `components/common/Form.js` will be added to the list, but only if those files exist.

Manually declaring assets [¶](https://jinjax.scaletti.dev/guides/css-and-js/#s-manually-declaring-assets)
---------------------------------------------------------------------------------------------------------

In addition to auto-loading assets, the CSS and/or JS of a component can be declared in the metadata header with `{#css ... #}` and `{#js ... #}`.

```
{#css lorem.css, ipsum.css #}
{#js foo.js, bar.js #}

```

-   The file paths must be relative to the root of your components catalog (e.g., `components/form.js`) or absolute (e.g., `http://example.com/styles.css`).
-   Multiple assets must be separated by commas.
-   Only one `{#css ... #}` and one `{#js ... #}` tag is allowed per component at most, but both are optional.

### Global assets [¶](https://jinjax.scaletti.dev/guides/css-and-js/#s-global-assets)

The best practice is to store both CSS and JS files of the component within the same folder. Doing this has several advantages, including easier component reuse in other projects, improved code readability, and simplified debugging.

However, there are instances when you may need to rely on global CSS or JS files, such as third-party libraries. In such cases, you can specify these dependencies in the component's metadata using URLs that start with either "/", "http://", or "https://".

When you do this, JinjaX will render them as is, instead of prepending them with the component's prefix like it normally does.

For example, this code:

```
{#css foo.css, bar.css, /static/bootstrap.min.css #}
{#js http://example.com/cdn/moment.js, bar.js  #}

{{ catalog.render_assets() }}

```

will be rendered as this HTML output:

```
<link rel="stylesheet" href="/static/components/foo.css">
<link rel="stylesheet" href="/static/components/bar.css">
<link rel="stylesheet" href="/static/bootstrap.min.css">
<script type="module" src="http://example.com/cdn/moment.js"></script>
<script type="module" src="/static/components/bar.js"></script>

```

Including assets in your pages [¶](https://jinjax.scaletti.dev/guides/css-and-js/#s-including-assets-in-your-pages)
-------------------------------------------------------------------------------------------------------------------

The catalog will collect all CSS and JS file paths from the components used on a "page" and store them in the `catalog.collected_css` and `catalog.collected_js` lists.

For example, after rendering this component:

components/MyPage.jinja

```
{#css mypage.css #}
{#js mypage.js #}

<Layout title="My page">
  <Card>
    <CardBody>
      <h1>Lizard</h1>
      <p>The Iguana is a type of lizard</p>
    </CardBody>
    <CardActions>
      <Button size="small">Share</Button>
    </CardActions>
  </Card>
</Layout>

```

Assuming the `Card` and `Button` components declare CSS assets, this will be the state of the `collected_css` list:

```
catalog.collected_css
['mypage.css', 'card.css', 'button.css']

```

You can add the `<link>` and `<script>` tags to your page automatically by calling `catalog.render_assets()` like this:

components/Layout.jinja

```
{#def title #}

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  {{ catalog.render_assets() }}
</head>
<body>
  {{ content }}
</body>
</html>

```

The variable will be rendered as:

```
<link rel="stylesheet" href="/static/components/mypage.css">
<link rel="stylesheet" href="/static/components/card.css">
<link rel="stylesheet" href="/static/components/button.css">
<script type="module" src="/static/components/mypage.js"></script>
<script type="module" src="/static/components/card.js"></script>
<script type="module" src="/static/components/button.js"></script>

```

Middleware [¶](https://jinjax.scaletti.dev/guides/css-and-js/#s-middleware)
---------------------------------------------------------------------------

The tags above will not work if your application can't return the content of those files. Currently, it can't.

For that reason, JinjaX includes WSGI middleware that will process those URLs if you add it to your application.

This is not needed if your components don't use static assets or if you serve them by other means.

```
from flask import Flask
from jinjax import Catalog

app = Flask(__name__)

# Here we add the Flask Jinja globals, filters, etc., like `url_for()`
catalog = jinjax.Catalog(jinja_env=app.jinja_env)

catalog.add_folder("myapp/components")

app.wsgi_app = catalog.get_middleware(
    app.wsgi_app,
    autorefresh=app.debug,
)

```

The middleware uses the battle-tested [Whitenoise library](http://whitenoise.evans.io/) and will only respond to the *.css* and *.js* files inside the component(s) folder(s). You must install it first:

```
pip install jinjax[whitenoise]

```

Then, you can configure it to also return files with other extensions. For example:

```
catalog.get_middleware(app, allowed_ext=[".css", ".js", ".svg", ".png"])

```

Be aware that if you use this option, `get_middleware()` must be called after all folders are added.

Good practices [¶](https://jinjax.scaletti.dev/guides/css-and-js/#s-good-practices)
-----------------------------------------------------------------------------------

### CSS Scoping [¶](https://jinjax.scaletti.dev/guides/css-and-js/#s-css-scoping)

The styles of your components will not be auto-scoped. This means the styles of a component can affect other components and likewise, they will be affected by global styles or the styles of other components.

To protect yourself against that, *always* add a custom class to the root element(s) of your component and use it to scope the rest of the component styles.

You can even use this syntax now supported by [all modern web browsers](https://caniuse.com/css-nesting):

```
.Parent {
  .foo { ... }
  .bar { ... }
}

```

The code above will be interpreted as

```
.Parent .foo { ... }
.Parent .bar { ... }

```

Example:

components/Card.jinja

```
{#css card.css #}

<div {{ attrs.render(class="Card") }}>
  <h1>My Card</h1>
  ...
</div>

```

components/card.css

```
/* 🚫 DO NOT do this */
h1 { font-size: 2em; }
h2 { font-size: 1.5em; }
a { color: blue; }

/* 👍 DO THIS instead */
.Card {
  & h1 { font-size: 2em; }
  & h2 { font-size: 1.5em; }
  & a { color: blue; }
}

/* 👍 Or this */
.Card h1 { font-size: 2em; }
.Card h2 { font-size: 1.5em; }
.Card a { color: blue; }

```

warning

Always use a class instead of an `id`, or the component will not be usable more than once per page.

### JS events [¶](https://jinjax.scaletti.dev/guides/css-and-js/#s-js-events)

Your components might be inserted in the page on-the-fly, after the JavaScript files have been loaded and executed. So, attaching events to the elements on the page on load will not be enough:

components/card.js

```
// This will fail for any Card component inserted after page load
document.querySelectorAll('.Card button.share')
  .forEach((node) => {
    node.addEventListener("click", handleClick)
  })

/* ... etc ... */

```

A solution can be using event delegation:

components/card.js

```
// This will work for any Card component inserted after page load
document.addEventListener("click", (event) => {
  if (event.target.matches(".Card button.share")) {
    handleClick(event)
  }
})
```