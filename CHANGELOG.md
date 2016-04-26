# Changelog

- [1.1.0](#oneonezero)
- [1.2.0](#onetwozero)

<a name="onetwozero"/>
### Pyglbuffers 1.2.0

- ##### Main module
    - Buffer format token changes to facilitate the itegration with pyshaders

<a name="oneonezero"/>
### Pyglbuffers 1.1.0

- ##### Main module
    - Remove the data attribute. Instead of using buffer.data[::], buffer[::] must be used.
      To initialize a buffer data, instead of using buffer.data = x, buffer.init(x) must be used.
- ##### Extensions
    - Nothing new