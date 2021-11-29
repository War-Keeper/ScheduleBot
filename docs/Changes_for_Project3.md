The following changes have been made to ScheduleBot
==========================================================
- Events can now be deleted through the deleteevent command. Previously events were permanent once scheduled by the user, and can now be easily removed once the event has passed.
- Events can now be edited. Previously the details of an event were permanent once initialized, which did not account for schedule changes or day-to-day randomness in people's lives. Now all details of an event can be changed through the editevent command, allowing for significant flexibility.
- Events can now be easily visualized through retrieveevent, which provides a graphical representation of events along with their start and end times. This makes schedules easy to parse at a glance.
- Event creation that uses buttons has been implemented. This significantly cuts down on the amount of typing a user has to do while creating events, and provides visual clarity during each step. This system also alleviates the need to enter event time twice, which was necessary on the old schedule command. Furthermore, a "Same Day" option has been added when scheduling events, streamlining a large chunk of the event creation process for events that start and end on the same date.
- Group Events have been added through reactions. Users can react to bot-posted messages in order to add events to their calendars simultaneously, eliminating the need for users to each create events themselves.
- Testing has been updated to use make use of conftest.py, which is set up before every test. This alleviates the need to declare fixtures in each testing file, greatly cutting down on the amount of code in each file.
- Significant html documentation for each command has been added, allowing developers to easily view all data about the command as well as source code in one location
- The !help command has been updated to accurately reflect changes
- Automatic code coverage has been changed to use codecov, which provides a cleaner interface and does not require a paid plan
- Numerous source files have been updated to remove minor bugs, syntax errors, and to clean up formatting.
- Added over 2.5k lines of code
