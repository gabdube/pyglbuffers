# Changelog

- [1.1.0](#oneonezero)

<a name="oneonezero"/>
### Pyglbuffers 1.1.0

- ##### Main module
    - Remove the data attribute. Instead of using buffer.data[::], buffer[::] must be used.
      To initialize a buffer data, instead of using buffer.data = x, buffer.init(x) must be used.
- ##### Extensions
    - Nothing new