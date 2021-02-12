Some JS developers don't know the differences between anonymous functions and arrow functions, and this misunderstanding sometimes leads to unintentional behavior.

You have to know that the anonymous function isn't the same as the arrow function, and to make that clear, let's have a look at the following Vue.js component:
```javascript
<template>
    <div>
        <ul>
            <li v-for="user in users">{{ user.first_name }} {{ user.last_name }}
</li>
        </ul>
    </div>
</template>

<script>
export default {
    name: "Users",
    
    data() {
        return {
            users: [],
        }
    },
    
    mounted() {
        axios('https://reqres.in/api/users').then(response => function() {
            this.users = response.data.data;
        })
    }
}
</script>
```

As you've noticed, the `users` should be populated with the `response.data.data` - *as soon as the component gets mounted* - , but it still and will always refer to an empty array.

So, what’s the problem?

The problem is that the `this` keyword doesn’t get rebound when using anonymous functions, let’s see what does that mean by inspecting the `this` as follows:
```javascript
mounted() {
    axios('https://reqres.in/api/users').then(function(response) {
        console.log(this);
    })
}
```

Output:
```text
Window {window: Window, self: Window, document: document, name: "", location: Location, ...}
```

As you’ve noticed, the `console.log(this)` returns the `Window` object and not the `Vue` object - *which, it should be because it’s running within a Vue instance* - .

Prior ES6, JS developers tend to solve this problem by declaring a variable that binds the `this` outside the anonymous function as follows:
```javascript
const self = this;
axios('https://reqres.in/api/users').then(function(response) {
	console.log(self); // Vue instanse
})
```

Another solution is to use the `bind` method:
```javascript
axios('https://reqres.in/api/users').then(function(response) {
	console.log(this);
}.bind(this)); // Binds Vue instanse
```

While both solutions work as expected, they seem to be quirky, therefore ES6 introduced the arrow functions.

Arrow functions will always bind the current `this` so you don’t need to use any of those tricks:
```javascript
axios('https://reqres.in/api/users').then(response => this.users = response.data.data);
```

Additionally, arrow functions use shorter syntax hence less code and more readability:
```javascript
const langs = ['PHP', 'JavaScript', 'Go', 'Python'];

// Short syntax, no need for parantheses and return statement. Only one line supported.
langs.map(lang => `I love ${lang} !`);

// Multiple arguments, you should use parantheses.
langs.map((item, key) => `${key} I love ${lang} !`);

// Multiple lines
langs.map((lang, key) => {
    // more lines goes here
    return `${key} I love ${lang} !`;
});
```

As I said, arrow function isn’t a replacement for anonymous function, let me explain that by an example:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Events</title>

    <style>
        .style2 {
            background-color: coral;
            color: white;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div id="app">
    Hello World
</div>

<script>
    const app = document.getElementById("app");

    app.addEventListener('click', function(event) {
        this.classList.toggle('style2');
    });
</script>
</body>
</html>
```

This example works perfectly, because the `this` refers to the `app` element and not the `Window` object, this means that `style2` will be toggled when the user clicks on the `app` element.

Let’s try to replace it by the arrow function:
```javascript
app.addEventListener('click', () => {
    this.classList.toggle('mystyle');
});
```

Output:
```text
Uncaught TypeError: Cannot read property 'toggle' of undefined ...
```

As you guessed by now, the arrow function refers to the `Window` object and not the `app` element.

I hope you enjoyed reading this short post!