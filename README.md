PyGLbuffers
===================


PyGLbuffers aims to completely wraps the opengl2.1 buffer api in a python module. 
PyGLbuffers provides a pythonic OOP api that hides the lower level (ctypes) calls. 
PyGLbuffers provides a high level api and a low level api, and it can be integrated easily with 
existing code because it does not occlude the underlying opengl values.

PyGLbuffers was programmed using very high standards. This means that PyGLbuffers 
is fully tested and it comes with an exhaustive documentation (this file). The code is DRYer 
than the Sahara and it makes uses of many advanced python functionalities to make the code 
smaller, easier to use and easier to read.

Note that this module do not includes wrapper over the opengl drawing functions. 
Such functions could be available in the future in form of extensions, but they will never be part of main module.

If this project interest you, you might also like [pyshaders](https://github.com/gabdube/pyshaders)

----------

- [PyGLbuffers](#)
	- [Requirements](#requirements)
	- [Installation](#installation)
		- [Pip](#pip)
		- [Manual](#manual)
	- [License](#license)
	- [Extensions](#extensions)
	  - [Overview](#extensions_overview)
	  - [Usage](#extensions_usage)
	  - [All extensions](#extensions_all)
	- [Programmer's Guide](#guide)
       - [Creation](#creation)
       - [Format](#format)
       - [Reading/Writing](#feed)
       - [Mapping](#mapping)
	- [API](#api)
	- [Future](#future)


<a name="requirements"></a>

**Requirements**
-------------
- Python >= 3.3
- An GPU that supports OpenGL 2.1 core
- Pyglet (any versions) <sub><sup>(See the Future section about supporting other libraries)</sup></sub>


<a name="installation"></a>

**Installation**
-------------

<a name="pip"></a>

### Pip
Run this command
>pip install pyglbuffers [--install-option="--no-extensions"]

<a name="manual"></a>

### Manual
1. Download the source
2. Copy **pyglbuffers.py** in your project
3. **Optionally** copy **pyglbuffers_extensions** in the same folder (see [extensions](#extensions))  

**or**

1. Download the source
2. Run **python setup.py install [--no_extensions]** 


<a name="license"></a>

License
-------------

>MIT License

>Copyright (c) 2016 Gabriel Dubé

>Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

>The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<a name="extensions"></a>

Extensions
-------------- 

<a name="extensions_overview"></a>

### Overview
By default, pyglbuffers only wraps the api of opengl 2.1. In order to wrap newer features 
that might not be supported on older hardware, pyglbuffers uses **extension modules**. 
Extensions modules are python modules located in the **pyglbuffers_extensions** package. 
These modules **must not be imported using the import keyword**, instead they are loaded 
using the **load_extension** function. load_extension checks if the client supports the 
extension and a few other things, if something is wrong **ImportError** or a **PyShadersExtensionError** error is raised.

Extensions modules must not be imported using the **import keyword** because an 
extension module by itself do nothing: their roles are to register new functionalities 
inside the pyglbuffers module.

Lastly, extensions **must be loaded before using the pyglbuffers api**. 

<a name="extensions_usage"></a>

### Usage

pyglbuffers offers three top levels functions to manage extensions.

```python
def extension_loaded(extension_name):
def check_extension(extension_name):
def load_extension(extension_name):
```

**extension_name** is any of the extension under [All Extensions](%extensions_all).

**extension_loaded** checks if an extension was loaded. An extension cannot be loaded more than once.  
**check_extension** checks if the client can use the extension  
**load_extension** loads the extension

Example:  
```python
from pyglbuffers import load_extension, extension_loaded,  check_extension, PyGlBuffersExtensionError
try:
    load_extension('copy_write_buffers')
except PyGlBuffersExtensionError:
    print("Your system do not meet the requirements to use this program")
    exit()
    
print(extension_loaded('copy_write_buffers'))
# True

print(check_extension('copy_write_buffers'))
# True
```

<a name="extensions_all"></a>  
### All extensions

No extension are available right now.


<a name="guide"></a>  
Programmer's Guide
-------------

<a name="creation"></a>  
#### **Creating buffers**

The **Buffer** class wrap most of the opengl buffer api. In order to create a buffer, different class methods can be called
with a buffer format and optionnaly an usage as parameters. By default the usage is set to GL_STATIC_DRAW.

The methods:  
```python
Buffer.array(format, usage=GL_STATIC_DRAW)        #GL_ARRAY_BUFFER
Buffer.element(format, usage=GL_STATIC_DRAW)      #GL_ELEMENT_ARRAY_BUFFER
Buffer.pixel_pack(format, usage=GL_STATIC_DRAW)   #GL_PIXEL_PACK_BUFFER
Buffer.pixel_unpack(format, usage=GL_STATIC_DRAW) #GL_PIXEL_UNPACK_BUFFER
```

** The binding point **  
Each of these methods create a buffer with a different default binding point. The binding point
is not static, it can be changed anytime by setting the field **target**. 
During the instanciation, the buffer object is bound to their binding point to finalize its creation.
The default binding point will be used for every methods that require the buffer to be bound. Most of the functions offers
to set the binding explicitly, with some exceptions. The most notable one is when
the python syntax is used to fill a buffer with data (see [writing to buffers](#feed)).
 
** The format **  
The buffer data is packed as raw c arrays of struct. In order to tell python how it should
pack/unpack the data, a BufferFormat is used. For convenience, a buffer format can be created from
a string. Buffer formats created from strings are cached. Ie: creating two buffer with the same
format will not create two buffer format object. For more details see [buffer formats](#format).

** Usage **  
The usage is no different from the opengl usage. It uses the same constants.

Example:  
```python
buffer = Buffer.array('(3f)[position](4f)(color)', GL_DYNAMIC_DRAW)
```

<a name="format"></a>  
#### **Buffer formats**

The buffer creation functions accept either a string representing a buffer format
or a buffer format object. If a string is passed, **BufferFormat.from_string** will be used
to create the object.

A format string is composed of N format token.  
A format token follow these rules: ({number}{format char})[{name}]  
Whitespaces are ignored. Ideally, a token name should match the shaders attribute vars.
The token names are also used when unpacking a buffer data. See [reading to buffers](#feed).

Available format char:

- f: float
- d: double
- b: byte
- B: unsigned Byte
- s: short
- S: unsigned short
- i: int
- I: unsigned int            

Example:

- "(3i)[vertex](4f)[color]"
- "(4f)[foo] (4f)[bar] (4d)[yolo]"



Buffers format can be cloned using the methods **BufferFormat.new**. The method also accept
a string (and from_string will be called). 

**Warnings**  
A buffer format must not be changed once data was written to it.  
While its possible to have any positive token length, a size of 1,2,3 or 4 should be used
because that how opengl wants its values formatted.

<a name="feed"></a>  
#### **Reading/Writing buffers**

The main purpose of pyglbuffers is to read and write to opengl buffers in a pythonic way. Reading and
writing is done using the python slice syntax.

**Initializing**  
The first thing to do after creating a buffer is to set its capacity. If the data is already available
it is possible to set the data directly by assigning a value to the **data** field. Of course, the data must match
the buffer format. If something does not match, an error will be raised.

```python
buffer = Buffer.array('(3f)[position](4f)(color)', GL_DYNAMIC_DRAW)
my_data = ((30,20,30), (1,1,1,1)), ((30,20,30), (1,1,1,1))

buffer.data = my_data
# or
buffer.data.buffer(my_data)
```

If the data is not available, it is possible to reserve space using **reserve**.
Reserve will reserve space for n elements in the buffer. Data will be zeroed.

```python
buffer = Buffer.array('(3f)[position](4f)(color)', GL_DYNAMIC_DRAW)

buffer.data.reserve(1000)
```

**Writing**  
Writing is done using the slice syntax on the buffer data field. Buffers do not
support implicit resizing, so assigning too much or not enough data will raise an error.

Each time data is written, the buffer is bound to the default binding point and 
glBufferSubData is called. This can become expensive if called multiple times. 
That's why it's possible to map the buffer. See [mapping](#mapping).

When the buffer is not mapped, slice steps other than "1" and "-1" are not supported.

```python
buffer = Buffer.array('(3f)[position](4f)(color)', GL_DYNAMIC_DRAW)
buffer.data.reserve(1000)

buffer.data[0:10] = ((1,1,1), (1,1,1,1))*10
buffer.data[10] = ((2,2,2), (2,2,2,2))
```

**Reading**  
Reading the buffer content is done the same way. The data is returned in named
tuples. 

Unlike writing, steps are supported even if the buffer is not mapped.

```python
buffer = Buffer.array('(3f)[position](4f)(color)', GL_DYNAMIC_DRAW)
buffer.data = ((5.0, 4.0, 83.32), (0.5, 0.5, 0.5, 0.5))

print(buffer.data[0])
# V(position=(5.0, 4.0, 83.32), color=(0.5, 0.5, 0.5, 0.5))
```

<a name="mapping"></a>  
#### **Mapping buffers**

Buffers can be mapped locally to increase the reading and the writing speed. It is done
using the map and the unmap methods or by using the python **with** syntax. Mapping use
glMapBuffer. 

Optionnaly, a buffer access can be specified. While opengl states that there is no
real restrictions even if you choose something different than GL_READ_WRITE, attempting
to read on a write only or writing on a read only buffer will raise an error.

When using the with syntax, the access is set to GL_READ_WRITE and the
binding point used is the default one.

```python
buffer.map()
#do stuff
buffer.unmap()

#or

with buffer:
    #do stuff
```

<a name="owned"></a>  
#### **Owned VS Borrowed**

The Buffer class is a wrapper over an opengl buffer. To do not leak ressouces, a buffer
is freed when the wrapper reference count reach zero. This means the wrapper own the ressouce.
Buffers created from the class methods (ex: **array**) owns the ressource by default.

When the Buffer class wrap a buffer that was not created by the api ([Integrating with existing code](#integrate)),
the owned property is set to false. This means that the buffer will not be freed after the object goes out of scope.

This can be changed anytime by setting the "owned" property.


<a name="integrate"></a>  
#### **Integrating with existing code**

It is possible to wrap existing buffers using the buffer constructor.

```python
#def __init__(self, buffer_id, format, usage=GL_DYNAMIC_DRAW, owned=False)

buffer = Buffer(my_buffer, '(4f)[foo]', owned=True)
```

- buffer_id is the opengl buffer identifier
- format must match the buffer data
- usage is the same hint used when creating buffers
- owned should be true if you want python to GC the buffer once it goes out of scope. (see [owned vs borrowed](#owned))

<a name="api"></a>  
**API**
-------------

<a name="buffer"/>  
### **Buffer**  
>**Buffer(object)**
Wrapper over an opengl buffer.
    
**Slots**:
>- *bid*: Underlying buffer identifier
>- *data*: Object that allows pythonic access to the buffer data
>- *target*: Buffer target (ex: GL_ARRAY_BUFFER)
>- *owned*: If the object own the underlying data
>
>**Readonly Properties**:  
>- *size*: Size of the buffer in bytes
>- *mapped*:  If the buffer is mapped or not
>- *access*:  Access flag when mapped
>- *usage*:  Usage flag

♣
>**Buffer.array(cls, format, usage=GL_STATIC_DRAW)**   
>**Buffer.element(cls, format, usage=GL_STATIC_DRAW)**   
>**Buffer.pixel_pack(cls, format, usage=GL_STATIC_DRAW)**   
>**Buffer.pixel_unpack(cls, format, usage=GL_STATIC_DRAW)**
>
> Generate a buffer. The default binding point depends on the method used.

♣
>**Buffer.valid(self)**  
>Return True if the wrapped value is a valid opengl buffer

♣
>**Buffer.bind(self, target=None)**  
>Bind the buffer to a target. If target is None, the default binding point is used

♣
>**Buffer.map(self, access=GL_READ_WRITE, target=None)**  
>Map the buffer locally. This increase the reading/writing speed.
>If the buffer was already mapped, a BufferError will be raised.
>
>Arguments:
>    access: Buffer access. Can be GL_READ_WRITE, GL_READ_ONLY, GL_WRITE_ONLY. Default to GL_READ_WRITE
>    target: Target to bind the buffer to. If None, use the buffer default target. Default to None.

♣
>**Buffer.unmap(self)**  
>Unmap the buffer. Will raise a BufferError if the buffer is not mapped.

♣
>**Buffer.__bool__(self)**  
>
>     bool(buffer)
>     
> Return True if the wrapped value is a valid opengl buffer

♣
>**Buffer.__len__(self)**  
>
>     len(buffer)
>     
> Return the number of elements in the buffer

### **BufferData**  
>**BufferData(object)**  
>Wrapper over an opengl buffer. Wraps data access in a pythonic way.
>This object is created with a Buffer and must not be instanced manually.
>

♣
>**BufferData.buffer(self, data)**  
>Fill the buffer data with "data". Data must be formatted using the
>parent buffer format. This calls glBufferData. To initialize a buffer
>without data (ie: only reserving space), use reserve().
>
>This method is called when assiging values to the data field of a buffer.
>Ex: buffer.data = ( (1.0, 2.0, 3.0, 4.0),  )
>
>Parameters:
>data: Data to use to initialize the buffer.

♣
>**BufferData.reserve(self, length)**  
>Fill the buffers with "length" zeroed elements.
>            
>Parameters:
>    length: Number of element the buffer will be able to hold

♣
>**Buffer__getitem__(self, key)**  
>
>     buffer.data[key]
>     
> Read the buffer data

♣
>**Buffer.__setitem__(self, key, value)**  
>
>     buffer.data[key] = value
>     
> Set the buffer data

♣
>**Buffer.__repr__(self)**  
>
>     repr(buffer)
>     
> Represent the buffer as a python list

### **BufferFormat**  
>**BufferFormat(object)**  
>This class has two functions:
>- Pack formatted python data into a raw buffer.
>- Read a formatted buffer and return formatted python data
>
>Fields:
>- *struct*: ctypes struct representing this format
>- *item*: named tuple representing this format
>- *tokens*: Information on the formatted values fields
>

♣
>**Buffer.from_string(cls, format_str)**  
>Create a buffer format from a string. Generated buffer format are
>cached, so this function is not expensive to call.
>
>A format string is composed of N format token.
>A format token follow these rules: ({number}{format char})[{name}]
>Whitespaces are ignored.
>
>Available format char:
>  f: float
>  d: double
>  b: byte
>  B: unsigned Byte
>  s: short
>  S: unsigned short
>  i: int
>  I: unsigned int            
>
>Example:
>    "(3i)[vertex](4f)[color]"
>    "(4f)[foo] (4f)[bar] (4d)[yolo]"

<a name="future"></a>  
**Future**
-------------

Could be added to the main module:

- "Metabuffers" buffers with multiple format
- Vertex attrib array "binding points" (for glVertexAttribPointer)

Could be added as an extension:

- Support for all the other buffer bindings
- Clear functions
- Interoptability with pyshaders
- Drawing functions




