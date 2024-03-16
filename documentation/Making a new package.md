># Porting a package from ROS to ROS2?
>I heavily recommend doing this by first creating a fresh new package [like below](#creating-a-new-ros2-package-for-smarc2). 
>This will create the bare minimums that you need with examples in every file.
>Then copy the _functionality_ of the old package to the new one.
>Then check out [this mini tutorial](./Porting%20a%20package.md) for more depth.
> 
>You can use [my journey notes](./media/SAM%20Humble%20Port.png) as a guide.
>It has links to related online documentation and the errors that I received and how I resolved them.
>See [the ported sam_basic_controllers package](../examples/sam_basic_controllers/) for an example ported package.


# Creating a new ROS2 package for SMaRC2
Navigate to where the new package will live, and use the command `ros2 pkg create --description <ONE LINE DESC> --license MIT --build-type {ament_cmake, ament_python} --maintainer-email <YOUR-EMAIL> --maintainer-name <YOUR-NAME> <PACKAGE-NAME>`

And then remove the auto-generated tests in the test directory.
Because for _our_ use cases, they will just be confusing _IMO_.

If your package is C++, use `ament_cmake`.

OR 

If your package needs message generation (then it should probably be in [the messages directory](../messages/)) then use `ament_cmake`. 
You can check out packages in [the messages directory](../messages/) for examples on how to configure `package.xml` and `CMakeLists.txt`.

`ament_cmake` is the basically the same as ros1 packages, with a few simplifying changes to how `CMakeLists.txt` is handled. 


If your package is _pure_ python, then use `ament_python`.
Pure python packages do not have `CMakeLists.txt`, instead they use `setup.py` to define where files should be installed. 
If something is not found, always start checking if that something is told where to go when building in `setup.py`.
Check out the [ros2_python_examples](../examples/ros2_python_examples/) package.
Also check [the python imports guide](./Python%20imports.md) if you're coming from ROS1.


If your package is a mix of C++ and python (**avoid this in the first place!**) then use `ament_cmake` and modify the `package.xml` and `CMakeLists.txt` to have `ament_cmake_python` manually.
See [the ported sam_basic_controllers package](../examples/sam_basic_controllers/)


## Messages
If your package requires a message, action or service definition, it is best placed in a package that contains only messages. 
If you think this definition will be used by multiple people/nodes, then placing it in the [general smarc_msgs repo](../messages/smarc_msgs/) should suffice. Otherwise consider creating a new package under [the messages directory](../messages/).

## Document
Write a [nice readme](./Writing%20a%20nice%20README.md) for your new package so that it can be used by others.
Don't forget that _you_ will forget things, and you will thank yourself in 2 months if you write this readme _now_.


## Test, test, test!
### Why?
Packages should come with tests. 
These tests should be runnable with `colcon test` locally.
Imagine a scenario where you changed your node and made a pull request. 
If your node is relied upon by some other person's node, that other person will be anxious. 
If you can show that other person that your changes did not make THEIR tests fail, that person will be relieved.
Thus, write tests around your nodes that you care about, such that other people can run ALL the tests ALL the time and make you happy that their changes did not break your stuff.

**The point is to test things you care about!**
Not every single internal function needs a test, our goal is not 100% code coverage!

The tests in individual packages are not meant to test the entire software stack, but to test the components.
*Notice that using the Model View Controller architecture will help you here immensely, since you can create mock objects for each that test the others very easily!*

Most of the time, the interaction between nodes at this level is going to be message/service/action related.
For ex: Person A uses modifies "RPM.msg:: int rpm" into "RPM.msg:: float rpm" for their node, this should make person B's tests fail due to the change and alert person A that if they want this change in the message, they should also modify person B's code to handle the new version.
This modification might lead to further tests failing/passing... and so on.


### How?
To run tests for a single package, and see the output nicely in the terminal, run: `colcon test --packages-select <PACKAGE_NAME> --event-handlers console_cohesion+`
Ignore the `packages-select` part to run _all_ tests in the colcon workspace.

### Python
Follow [the ROS-Humble tutorial](https://docs.ros.org/en/humble/Tutorials/Intermediate/Testing/Python.html)

[ros2_python_examples](../examples/ros2_python_examples/test/) has one file that has 2 tests, one that will always fail and one that will always succeed. 
Notice the lack of auto-generated `flake8`, `pep` and `copyright` tests.
These are usually a little too strict about formatting and such, so either learn to modify them to check the things you care about or simply remove them to reduce the nagging.

Anything in here named `test_XXX.py` with functions `test_AAA` will be run when `colcon test` is run. Simply use assertions to pass/fail.


### Cpp
Follow [the ROS-Humble tutorial](https://docs.ros.org/en/humble/Tutorials/Intermediate/Testing/Cpp.html)
