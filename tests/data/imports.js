// Import an entire module's contents
// Import a single export from a module
// Import multiple exports from module
// Import an export with a more convenient alias
// Rename multiple exports during import
// Importing defaults
// Namespace import
// Specific named imports
// Import a module for its side effects only
import '/modules/my-module.js';

// Dynamic imports
(async () => {
    if (somethingIsTrue) {
        // import module for side effects
        await import('/modules/my-module.js');
    }
})();

// dynamic namespace imports
(async () => {
    if (somethingIsTrue) {
        const { default: myDefault, foo, bar } = await import('/modules/my-module.js');
    }
})();

// Dynamic Imports
import('/modules/my-module.js')
.then((module) => {
    // Do something with the module.
});

let module = await import('/modules/my-module.js');
