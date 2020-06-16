// Default + Namespace import
import myDefault, * as myModule from '/modules/my-module.js';

// Importing defaults
import myDefault from '/modules/my-module.js';

// Import an entire module's contents
import * as myModule from '/modules/my-module.js';

// Aliasing a default
import { default as alias } from "asynckit";

// Import a single export from a module
import { myExport } from '/modules/my-module.js';

// Import a module for its side effects only
import '/modules/my-module.js';

// Rename multiple exports during import
import {
    reallyReallyLongModuleExportName as shortName,
    anotherLongModuleName as short
} from "/modules/my-module.js";

// Import an export with a more convenient alias
import { reallyReallyLongModuleExportName as shortName }
    from '/modules/my-module.js';

// Import multiple exports from module
import {foo, bar} from '/modules/my-module.js';

// Specific named imports
import myDefault, {foo, bar} from '/modules/my-module.js';

// Dynamic Imports
import('/modules/my-module.js')
    .then((module) => {
        // Do something with the module.
    });

// dynamic namespace imports
(async () => {
    if (somethingIsTrue) {
        const { default: myDefault, foo, bar } = await import('/modules/my-module.js');
    }
})();

// Dynamic imports
(async () => {
    if (somethingIsTrue) {
        // import module for side effects
        await import('/modules/my-module.js');
    }
})();

let module = await import('/modules/my-module.js');
