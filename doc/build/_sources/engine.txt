Engine classes and methods
==========================

Plug methods list
-----------------

| :ref:`Plug.connect-section`
| :ref:`Plug.disconnect-section`
| :ref:`Plug.generate_name-section`
| :ref:`Plug.set-section`

Circuit methods list
--------------------

| :ref:`Circuit.class_name-section`
| :ref:`Circuit.evalfun-section`
| :ref:`Circuit.generate_name-section`
| :ref:`Circuit.nb_inputs-section`
| :ref:`Circuit.nb_outputs-section`
| :ref:`Circuit.remove-section`
| :ref:`Circuit.setName-section`

Plug methods descriptions
-------------------------

..  _Plug.connect-section:

Plug.connect(other)
^^^^^^^^^^^^^^^^^^^

..  method::  Plug.connect(other)

    Connects two plugs, or logs a warning message if the connection isn't valid.
   
    :param other: the second plug of the connection
    :type other: Plug
    :return: True if the connection has been established, False otherwise
    :rtype: bool

    exemple::
    
        plugA.connect(plugB)
        => True if plugA has been connected to plugB

..  _Plug.disconnect-section:

Plug.disconnect(other)
^^^^^^^^^^^^^^^^^^^^^^

..  method::  Plug.disconnect(other)

    Disconnects two plugs, or logs a warning message if the disconnection isn't valid.
   
    :param other: the second plug of the disconnection
    :type other: Plug
    :return: True if the has been successfully disconnected, False otherwise
    :rtype: bool

    exemple::
    
        plugA.disconnect(plugB)
        => True if plugB has been disconnected from plugA

..  _Plug.generate_name-section:

Plug.generate_name()
^^^^^^^^^^^^^^^^^^^^

..  method::  Plug.generate_name()

    Generate a name for the object.
    This method is called in the Plug constructor if no name was given to it. The generated name begin with 'in' or 'out' whether the Plug is an input or an output and ends with a number so that there cannot be two identical Plug names belonging to the same parent Circuit.
   
    :return: The generated name
    :rtype: str

    exemple::
    
        plugA.generate_name()
        => out3

..  _Plug.set-section:

Plug.set(value)
^^^^^^^^^^^^^^^

..  method::  Plug.set(value)

    Sets the boolean value of a Plug.
    True or 1 means that the power applied to the Plug is high. False or 0 means that the power is Low.
   
    :param value: The plug electric power value
    :type value: bool

    exemple::
    
        plugA.set(1)

..  _Plug.setName-section:

Plug.setName(name)
^^^^^^^^^^^^^^^^^^

..  method::  Plug.setName(name)

    Sets the object's name.
    The name cannot be empty or used by another Plug of the parent Circuit.
   
    :param name: The object's name
    :type name: str
    :return: True if the object's name has been successfully set, False otherwise
    :rtype: bool

    exemple::
    
        plugA.setName('myInputPlug')

Circuit methods descriptions
----------------------------

..  _Circuit.class_name-section:

Circuit.class_name()
^^^^^^^^^^^^^^^^^^^^

..  method::  Circuit.class_name()

    Retrieve the class name of the object.
    It is usefull to get the name of a Circuit subclass (gates).
   
    :return: The object class name
    :rtype: str

    exemple::
    
        circuitA.class_name()
        => AndGate

..  _Circuit.evalfun-section:

Circuit.evalfun()
^^^^^^^^^^^^^^^^^

..  method::  Circuit.evalfun()

    The evalfun method contains a function which must compute and set the object's output(s) value(s) based on the object input(s) value(s).
   
    :return: The object class name
    :rtype: str

    ..  note::
    
        Only Circuit subclass (gates) have an evalfun method. For instance, the NotGate Circuit subclass have an evalfun method which sets its output to be the logic negation of its input. 

..  _Circuit.generate_name-section:

Circuit.generate_name()
^^^^^^^^^^^^^^^^^^^^^^^

..  method::  Circuit.generate_name()

    Generate a name for the Circuit.
    This method is called in the Circuit constructor if no name was given to it. The generated name begin with the object class name and ends with a number so that there cannot be two identical Circuit names belonging to the same parent Circuit.
   
    :return: The generated name
    :rtype: str

    exemple::
    
        circuitA.generate_name()
        => XorGate2

..  _Circuit.nb_inputs-section:

Circuit.nb_inputs()
^^^^^^^^^^^^^^^^^^^

..  method::  Circuit.nb_inputs()

    Get the inputs number of the Circuit.
   
    :return: The inputs number
    :rtype: int

    exemple::
    
        circuitA.nb_inputs()
        => 6

..  _Circuit.nb_outputs-section:

Circuit.nb_outputs()
^^^^^^^^^^^^^^^^^^^^

..  method::  Circuit.nb_outputs()

    Get the outputs number of the Circuit.
   
    :return: The outputs number
    :rtype: int

    exemple::
    
        circuitA.nb_outputs()
        => 2

..  _Circuit.remove-section:

Circuit.remove(component)
^^^^^^^^^^^^^^^^^^^^^^^^^

..  method::  Circuit.remove(component)

    Remove a component from the object.
    The component can be a Plug or a Circuit. If it is a Plug the method will operate Plugs disconnections before removing the Plug so that it is fully removd from anywhere.
   
    :param component: The component to remove from the object
    :type component: Plug or Circuit
    :return: True if the component has been successfully removed from the object
    :rtype: bool

    exemple::
    
        circuitA.remove(plugA)

..  _Circuit.setName-section:

Circuit.setName(name)
^^^^^^^^^^^^^^^^^^^^^

..  method::  Circuit.setName(name)

    Sets the object's name.
    The name cannot be empty or used by another Plug of the parent Circuit.
   
    :param name: The object's name
    :type name: str
    :return: True if the object's name has been successfully set, False otherwise
    :rtype: bool

    exemple::
    
        circuitA.setName('AND_1')























