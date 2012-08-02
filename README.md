Usage
=====

Search for a template and import it. This performs a nodeCopy from file into the
current script and places the nodes laid out next to the first viewer it finds in
the graph.

Publish copies out the selected nodes to the file system and publishes the file to
Shotgun using tanks utility function.


Current Issues
==============

* Tags is currently added a plain text field, this needs to be updated to use the
  tagging metadata system in Shotgun.

* The publish dialog currently loads from Shotgun inline. This needs to be broken
  out into a worker thread.

* Ensure that any ui hacks have been propogated back to the ui files and saved to
  permit them to be renderated.
