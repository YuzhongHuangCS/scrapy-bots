# The user side implementation hasn't be decided.
# Two plans:

* Web
  1. Could make use of notification and websockets.
  2. User could set some keywords he wants to moniter, have a look on current result, then pin the tab.
  3. Send notification once new matched posts detected.

* Qt
  1. Native program means free to use system tray, system notification, even auto-start.
  2. Similar to web version, user could set keywords to moniter, have a look on the result, then hide the program.
  3. The program could pop up once new matched posts detected.
  4. Have to use polling to get the new posts, anything better?
  

  

