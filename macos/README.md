`sd2ui` is a MacOS menu bar extra application that controls `sd2`. Currently only
a few basic operations are supported:

- Show if the `sd2` daemon is running
- start/stop the `sd2` daemon
- kick off directory synchronization
- kick off container creation

All these operation are available from the command line as well by just
passing arguments to the `sd2` executable.

## How to build sd2ui
1. Make sure you have the latest XCode installed
2. Run `make macos-build` to build it. The `sd2ui` executable will be in 
`macos/build/Release/sd2ui.app/Contents/MacOS/sd2ui`