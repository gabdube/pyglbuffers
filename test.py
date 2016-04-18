# -*- coding: utf-8 -*-

import unittest, gc
from ctypes import byref

import pyglet
from pyglet.gl import (glIsBuffer, glGenBuffers, GLuint, GL_TRUE, GL_FALSE,
  glDeleteBuffers, GLfloat, GLubyte, glBindBuffer, GL_ARRAY_BUFFER)

import pyglbuffers
from pyglbuffers import (Buffer, BufferFormat, BufferFormatError, GL_READ_WRITE,
  GL_STATIC_DRAW, GL_DYNAMIC_COPY, GL_DYNAMIC_DRAW, GL_READ_ONLY, GL_WRITE_ONLY,
  eval_index, eval_slice, load_extension, check_extension, PyGlBuffersExtensionError,
  extension_loaded)

def create_raw_buffer():
    buf = GLuint()
    glGenBuffers(1, byref(buf))
    glBindBuffer(GL_ARRAY_BUFFER, buf)
    return buf.value
    
    
class TestIndexEvaluator(unittest.TestCase):
    
    def test_eval_index(self):
        " Test eval index "
        length = 30
        
        self.assertEqual(5, eval_index(5, length))
        self.assertEqual(25, eval_index(-5, length))
        
        with self.assertRaises(IndexError) as err1:
            eval_index(300, length)
            
        with self.assertRaises(IndexError) as err2:
            eval_index(-300, length)
            
        self.assertEqual('Index "300" out of bound, buffer has a length of "30"', str(err1.exception))
        self.assertEqual('Index "-300" out of bound, buffer has a length of "30"', str(err2.exception))
        
    def test_eval_slice(self):
        " Test eval slice "
        length = 30
        
        self.assertEqual((1, 5, 2), eval_slice(slice(1,5,2), length))
        self.assertEqual((0, 30, 1), eval_slice(slice(None), length))
        self.assertEqual((0, 25, 1), eval_slice(slice(25), length))
        self.assertEqual((5, 30, 1), eval_slice(slice(5, None), length))
        self.assertEqual((0, 5, 1), eval_slice(slice(None, 5), length))
        self.assertEqual((25, 28, 1), eval_slice(slice(-5, -2), length))
        self.assertEqual((5, 8, -1), eval_slice(slice(8, 5, -1), length))
    
        with self.assertRaises(IndexError) as err1:
            eval_slice(slice(1, 1, 0), length)
            
        with self.assertRaises(IndexError) as err2:
            eval_slice(slice(1, 300), length)
            
        with self.assertRaises(IndexError) as err3:
            eval_slice(slice(300, 10), length)
            
        with self.assertRaises(IndexError) as err2:
            eval_slice(slice(1, 300), length)
            
        with self.assertRaises(IndexError) as err3:
            eval_slice(slice(300, 10), length)
            
        with self.assertRaises(IndexError) as err4:
            eval_slice(slice(1, -300), length)
            
        with self.assertRaises(IndexError) as err5:
            eval_slice(slice(-300, 10), length)
            
        self.assertEqual('Step cannot be 0', str(err1.exception))
        self.assertEqual('Slices indexes "1:300" out of bound, buffer has a length of "30"', str(err2.exception))
        self.assertEqual('Slices indexes "300:10" out of bound, buffer has a length of "30"', str(err3.exception))
        self.assertEqual('Slices indexes "1:-300" out of bound, buffer has a length of "30"', str(err4.exception))
        self.assertEqual('Slices indexes "-300:10" out of bound, buffer has a length of "30"', str(err5.exception))
    
class TestBuffersFormat(unittest.TestCase):
    
    def test_fromstring(self):
        
        f1 = BufferFormat.from_string("(3f)[foo]")
        f2 = BufferFormat.from_string("(3f)[vertex](4B)[color](3f)[normals]")
        f3 = BufferFormat.from_string(" (3 f)[b  ar](   2 B)[wa ll  et] ")    #Spaces are ignored
        
        self.assertIsInstance(f1, BufferFormat, "Buffer is not of type Buffer")  
        self.assertIsInstance(f2, BufferFormat, "Buffer is not of type Buffer")  
        self.assertIsInstance(f3, BufferFormat, "Buffer is not of type Buffer")  
        
        f1_fields = f1.struct._fields_
        f2_fields = f2.struct._fields_ 
        f3_fields = f3.struct._fields_ 
        
        self.assertEqual(1, len(f1.tokens), 'f1 should have 1 token')
        self.assertEqual(3, len(f2.tokens), 'f2 should have 3 tokens')
        self.assertEqual(2, len(f3.tokens), 'f3 should have 2 tokens')
        
        self.assertEqual([[3, GLfloat*3, 'foo']], [list(i) for i in f1.tokens])
        self.assertEqual([[3, GLfloat*3, 'vertex'], [4, GLubyte*4, 'color'], [3, GLfloat*3, 'normals']], [list(i) for i in f2.tokens])
        self.assertEqual([[3, GLfloat*3, 'bar'], [2, GLubyte*2, 'wallet']], [list(i) for i in f3.tokens])
        
        self.assertIn('foo', dir(f1.item), 'foo is not in the format items')
        self.assertIn('vertex', dir(f2.item), 'vertex is not in the format items')
        self.assertIn('color', dir(f2.item), 'color is not in the format items')
        self.assertIn('normals', dir(f2.item), 'normals is not in the format items')
        self.assertIn('bar', dir(f3.item), 'bar is not in the format items')
        self.assertIn('wallet', dir(f3.item), 'wallet is not in the format items')
        
        self.assertEqual(['foo'], [f[0] for f in f1_fields], 'fields names of the f1 struct do not match')
        self.assertEqual(['vertex', 'color', 'normals'], [f[0] for f in f2_fields], 'fields names of the f2 struct do not match')    
        self.assertEqual(['bar', 'wallet'], [f[0] for f in f3_fields], 'fields names of the f3 struct do not match')    
        
        self.assertEqual([GLfloat*3], [f[1] for f in f1_fields], 'fields types of the f1 struct do not match')
        self.assertEqual([GLfloat*3, GLubyte*4, GLfloat*3], [f[1] for f in f2_fields], 'fields types of the f2 struct do not match')
        self.assertEqual([GLfloat*3, GLubyte*2], [f[1] for f in f3_fields], 'fields types of the f3 struct do not match')
        
    def test_fromstring_fail(self):
        "Test if invalid format string fails"
        
        with self.assertRaises(BufferFormatError) as cm1:
            BufferFormat.from_string("")
            
        with self.assertRaises(BufferFormatError) as cm2:
            BufferFormat.from_string("(4k)[lolwat](2f)[aaa]")

        with self.assertRaises(BufferFormatError) as cm3:
            BufferFormat.from_string("(-5f)[lolwat]")
        
        with self.assertRaises(BufferFormatError) as cm4:
            BufferFormat.from_string("(2f)[ ]")
            
        with self.assertRaises(ValueError) as cm5:
            BufferFormat.from_string("(2f)[23d]")
            
        self.assertEqual('Format must be present', str(cm1.exception), 'Exception do not match')
        self.assertEqual('Format string is not valid', str(cm2.exception), 'Exception do not match')
        self.assertEqual('Format string is not valid', str(cm3.exception), 'Exception do not match')
        self.assertEqual('Format string is not valid', str(cm4.exception), 'Exception do not match')
        self.assertEqual('"23d" is not a valid variable name', str(cm5.exception), 'Exception do not match')
        
    def test_pack_single(self):
        " Test packing data into a struct " 
        f1 = BufferFormat.from_string('(3f)[foo]')
        f2 = BufferFormat.from_string('(3f)[vertex](4B)[color]')
        f3 = BufferFormat.from_string('(1d)[boo]')
        
        f1pd = f1.pack_single((1.0, 2.0, 3.0)) 
        f2pd = f2.pack_single( ((1.0, 2.0, 3.0), (255, 100, 200, 140)) )  
        f3pd = f3.pack_single((6666.0,))  
        
        self.assertIsInstance(f1pd, f1.struct)
        self.assertIsInstance(f2pd, f2.struct)
        self.assertIsInstance(f3pd, f3.struct)
        
        self.assertEqual((1.0, 2.0, 3.0), tuple(f1pd.foo))
        self.assertEqual((1.0, 2.0, 3.0), tuple(f2pd.vertex))
        self.assertEqual((255, 100, 200, 140), tuple(f2pd.color))
        self.assertEqual((6666.0,), tuple(f3pd.boo))
        
    def test_pack(self):
        " Test packing data into struct "
        f1 = BufferFormat.from_string('(3f)[foo]')
        f2 = BufferFormat.from_string('(3f)[vertex](4B)[color]')
        f3 = BufferFormat.from_string('(1d)[boo]')
        
        data1 = ( (1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0) )
        f1pd = f1.pack(data1)
        
        data2 = ( ((1.0, 2.0, 3.0), (215, 200, 230, 255)),
                  ((10.0, 8.0, 43.0), (100, 255, 50, 50)) )
        f2pd = f2.pack(data2)     
        
        data3 = [(x,) for x in (2, 70, 900.0, 823.0)]
        f3pd = f3.pack(data3)
        
        for index, d1 in enumerate(f1pd):
            self.assertEqual(data1[index], tuple(d1.foo))
            
        for index, d2 in enumerate(f2pd):
            self.assertEqual(data2[index][0], tuple(d2.vertex))
            self.assertEqual(data2[index][1], tuple(d2.color))
        
        for index, d3 in enumerate(f3pd):
            self.assertEqual(data3[index], tuple(d3.boo))
            
    def test_partial_pack(self):
        " Test pack with incomplete data"
        f1 = BufferFormat.from_string('(3f)[foo]')

        data1 = ( (1.0,), (4.0, 5.0, 6.0), (7.0, 8.0) )
        f1pd = f1.pack(data1)
        
        self.assertEqual((1.0, 0.0, 0.0), tuple(f1pd[0].foo))
        self.assertEqual((4.0, 5.0, 6.0), tuple(f1pd[1].foo))
        self.assertEqual((7.0, 8.0, 0.0), tuple(f1pd[2].foo))
        
    def test_unpack_single(self):
        " Test unpack single value"
        f1 = BufferFormat.from_string('(3f)[foo]')
        f2 = BufferFormat.from_string('(3f)[vertex](4B)[color]')
        
        f1pd = f1.pack_single((1.0, 2.0, 3.0)) 
        f2pd = f2.pack_single( ((1.0, 2.0, 3.0), (255, 100, 200, 140)) )  
        f2upd = f2.unpack_single(f2pd)    
        f1upd = f1.unpack_single(f1pd) 
        
        self.assertIsInstance(f1upd, f1.item)
        self.assertIsInstance(f2upd, f2.item)
        
        self.assertEqual((1.0, 2.0, 3.0), f1upd.foo)
        self.assertEqual((1.0, 2.0, 3.0), f2upd.vertex)
        self.assertEqual((255, 100, 200, 140), f2upd.color)
        
    def test_unpack(self):
        " Test unpack multiple values "
        f1 = BufferFormat.from_string('(3f)[foo]')
        f2 = BufferFormat.from_string('(3f)[vertex](4B)[color]')
        
        data1 = ( (1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0) )
        f1pd = f1.pack(data1)
        f1upd = f1.unpack(f1pd)      
        
        data2 = ( ((1.0, 2.0, 3.0), (215, 200, 230, 255)),
                  ((10.0, 8.0, 43.0), (100, 255, 50, 50)) )
        f2pd = f2.pack(data2)   
        f2upd = f2.unpack(f2pd)    
        
        for index, d1 in enumerate(data1):
            self.assertEqual(d1, f1upd[index].foo)
            
        for index, d2 in enumerate(data2):
            self.assertEqual(d2[0], f2upd[index].vertex)
            self.assertEqual(d2[1], f2upd[index].color)
        
    def test_unpack_fail(self):
        " Test upacking bad data data"
        f1 = BufferFormat.from_string('(3f)[foo]')
        f2 = BufferFormat.from_string('(3i)[foo]')
        
        data = ( (1,2,3), (4,5,6), (7,8,9) )
        f2pd = f2.pack(data)
        
        with self.assertRaises(ValueError, msg='Unpack was successful') as cm1:
            f1.unpack(f2pd)
            
        self.assertEqual('Impossible to unpack data that was not packed by the formatter',
                         str(cm1.exception), 'Exception do not match.')
        
    def test_pack_fail(self):
        " Test packing data with invalid format"
        f1 = BufferFormat.from_string("(3f)[foo]")
        f2 = BufferFormat.from_string("(3f)[vertex](4B)[color]")
        
        with self.assertRaises(ValueError, msg="Assign succeed") as cm1:
            data = ( (None,None,None), (None,None,None) )
            f1.pack(data)
            
        with self.assertRaises(IndexError, msg="Assign succeed") as cm2:
            data = ( (4.0, 5.0, 6.0, 12.0), )
            f1.pack(data)
            
        with self.assertRaises(ValueError, msg="Assign succeed") as cm3:
            f1.pack(())

        with self.assertRaises(ValueError, msg="Assign succeed") as cm4:
            data = ( ((10.0, 20.0, 30.0), (10, 11, 12, 13)), (20.0, 30.0, 40.0) )
            f2.pack(data)
             
        self.assertEqual('Expected Sequence with format "3f", found "(None, None, None)"', str(cm1.exception), 'Exceptions do not match')
        self.assertEqual('invalid index', str(cm2.exception), 'Exceptions do not match')
        self.assertEqual('No data to pack', str(cm3.exception), 'Exceptions do not match')
        self.assertEqual('Expected Sequence with format "3f", found "20.0"', str(cm4.exception), 'Exceptions do not match')
        
    def test_fromstring_cache(self):
        " Returned format should be cached "
        f1 = BufferFormat.from_string("(3f)[foo]")
        f2 = BufferFormat.from_string("(3f)[foo]")
        self.assertIs(f1, f2)
        

class TestBuffers(unittest.TestCase):
    
    def test_create(self):
        " Test buffer creation "
        buf1 = Buffer.array('(4f)[foo]')
        buf2 = Buffer.element('(4f)[foo]')
        buf3 = Buffer.pixel_pack('(4f)[foo]')
        buf4 = Buffer.pixel_unpack('(4f)[foo]')
        buf5 = Buffer.array('(4f)[foo]', usage=GL_DYNAMIC_COPY)
        
        buffers = (buf1, buf2, buf3, buf4, buf5)
        for buf in buffers:
            self.assertEqual(GL_STATIC_DRAW, buf.usage, 'Buffer default usage do not match')
            self.assertEqual(GL_READ_WRITE, buf.access, 'Buffer default access do not match')
        
        for buf in buffers:
            self.assertIsInstance(buf, Buffer, 'Buffer is not of type Buffer')
            self.assertNotEqual(0, buf.bid, 'Buffer id should not be 0')
            
    def test_valid(self):
        ' Test if generated buffers are valid '
        buf1 = Buffer.array('(4f)[foo]')  
        buf2 = Buffer(8883, '(4f)[foo]')
        
        self.assertTrue(buf1.valid(), 'Buffer 1 is not valid')
        self.assertTrue(buf1, 'Buffer 1 is not valid')
        self.assertFalse(buf2.valid(), 'Buffer 2 is valid')
        self.assertFalse(buf2, "Buffer 2 is valid")
        
    def test_reserve(self):
        ' Test reserve '
        buf1 = Buffer.array('(4f)[foo]', usage=GL_DYNAMIC_DRAW)  
        buf1.data.reserve(200)
        
        self.assertEqual(GL_DYNAMIC_DRAW, buf1.usage)
        self.assertEqual(200, len(buf1))
        self.assertEqual(3200, buf1.size)
        
    def test_get_set(self):
        " Test Get/Set on unmapped buffers"
        buf1 = Buffer.array('(4f)[foo]', usage=GL_DYNAMIC_DRAW)
        
        self.assertEqual(GL_STATIC_DRAW, buf1.usage)
        self.assertEqual(0, len(buf1))
        self.assertEqual(0, buf1.size)
        
        buf1.data = [(y,)*4 for y in [x for x in range(10)]]
        
        self.assertEqual(GL_DYNAMIC_DRAW, buf1.usage)
        self.assertEqual(10, len(buf1))
        self.assertEqual(160, buf1.size)
        
        get = lambda x, y, z: tuple([x.foo for x in buf1.data[x:y:z]])  
        
        self.assertEqual((0,0,0,0), buf1.data[0].foo)
        self.assertEqual(((1,1,1,1), (2,2,2,2)), get(1,3,1))
        self.assertEqual(((1,1,1,1), (3,3,3,3)), get(1,4,2))
        
        buf1.data[0] = (10,)*4
        buf1.data[1] = ((11,)*4,)
        buf1.data[2:5] = ((12,)*4, (13,)*4, (14,)*4)
        buf1.data[8:5:-1] = ((15,)*4, (16,)*4, (17,)*4,)
        
        self.assertEqual((10,10,10,10), buf1.data[0].foo)
        self.assertEqual((11,11,11,11), buf1.data[1].foo)
        
        for i, j in zip(buf1.data[2:5], ((12,)*4, (13,)*4, (14,)*4)):
            self.assertEqual(j, i.foo)
            
        for i, j in zip(buf1.data[8:5:-1], ((15,)*4, (16,)*4, (17,)*4)):
            self.assertEqual(j, i.foo)
            
    def test_get_set_mapped(self):        
        buf1 = Buffer.array('(4f)[foo]', usage=GL_DYNAMIC_DRAW)
        buf1.data = [(y,)*4 for y in [x for x in range(10)]]
        
        get = lambda x, y, z: tuple([x.foo for x in buf1.data[x:y:z]])          
        
        self.assertEqual(GL_FALSE, buf1.mapped)        
        with buf1:
            self.assertEqual(GL_TRUE, buf1.mapped)

            self.assertEqual((0,0,0,0), buf1.data[0].foo)
            self.assertEqual(((1,1,1,1), (2,2,2,2)), get(1,3,1))
            self.assertEqual(((1,1,1,1), (3,3,3,3)), get(1,4,2))
            
            buf1.data[0] = (10,)*4
            buf1.data[1] = ((11,)*4,)
            buf1.data[2:5] = ((12,)*4, (13,)*4, (14,)*4)
            buf1.data[8:5:-1] = ((15,)*4, (16,)*4, (17,)*4,)
            
        self.assertEqual(GL_FALSE, buf1.mapped)  
        
        self.assertEqual((10,10,10,10), buf1.data[0].foo)
        self.assertEqual((11,11,11,11), buf1.data[1].foo)
        
        for i, j in zip(buf1.data[2:5], ((12,)*4, (13,)*4, (14,)*4)):
            self.assertEqual(j, i.foo)

        for i, j in zip(buf1.data[8:5:-1], ((15,)*4, (16,)*4, (17,)*4)):
            self.assertEqual(j, i.foo)
            
    
    def test_get_set_fail(self):
        " Test Get/Set with bad values"
        buf1 = Buffer.array('(4f)[foo]', usage=GL_DYNAMIC_DRAW)
        buf1.data = [(y,)*4 for y in [x for x in range(3)]]
        
        buf2 = Buffer.array('(4f)[foo]')
        
        with self.assertRaises(KeyError) as err1:
            buf1.data[None]
            
        with self.assertRaises(ValueError) as err2:
            buf1.data[0:2] = ((12,)*4, (13,)*4, (14,)*4)
            
        with self.assertRaises(NotImplementedError) as err3:
            buf1.data[0:2:2] = (1,1,1,1)
            
        with self.assertRaises(IndexError) as err4:
            buf2.data[0:3] = [1,2] 
            
        self.assertEqual('\'Key must be an integer or a slice, got NoneType\'', str(err1.exception))
        self.assertEqual('Buffer do not support resizing', str(err2.exception))
        self.assertEqual('Unmapped buffer write do not support steps different than 1.', str(err3.exception))
        self.assertEqual('Slices indexes "0:3" out of bound, buffer has a length of "0"', str(err4.exception))
        
    def test_freeing(self):
        " Test freeing buffer "
        buf1 = Buffer.array('(4f)[foo]')  
        bid1 = buf1.bid
        data = buf1.data
        
        buf2 = Buffer(create_raw_buffer(), '(4f)[foo]', owned=False)
        bid2 = buf2.bid
        
        del buf1
        del buf2
        gc.collect()
        
        self.assertEqual(GL_FALSE, glIsBuffer(bid1), 'Buffer is still valid')
        self.assertEqual(GL_TRUE, glIsBuffer(bid2), 'Buffer is not valid')
        
        with self.assertRaises(RuntimeError, msg="Buffer is still alive") as cm1:
            data.buffer( ((1.0, 2.0, 3.0, 4.0),) )
            
        with self.assertRaises(RuntimeError, msg="Buffer is still alive") as cm2:
            data[0]
            
        with self.assertRaises(RuntimeError, msg="Buffer is still alive") as cm3:
            data[0] = (20.0, 2.0, 3.0, 4.0),
            
        self.assertEqual('Buffer was freed', str(cm1.exception), msg='Exception do not match')
        self.assertEqual('Buffer was freed', str(cm2.exception), msg='Exception do not match')
        self.assertEqual('Buffer was freed', str(cm3.exception), msg='Exception do not match')
        
        glDeleteBuffers(1, byref(bid2))
        
class TestExtensions(unittest.TestCase):
     
    def test_load(self):
        " Test extension loading "
        
        with self.assertRaises(ImportError) as cm1:
            load_extension('foo_bar')        
        
        with self.assertRaises(PyGlBuffersExtensionError) as cm2:
            load_extension('create_mmo')
                  
        
        self.assertEqual('No extension named "foo_bar" found', str(cm1.exception), 'Exception do not matches')
        self.assertEqual('Extension "create_mmo" is not supported', str(cm2.exception), 'Exception do not matches')
        
        self.assertNotIn('create_mmo', pyglbuffers.LOADED_EXTENSIONS, 'Extension name is in the loaded extensions')
        self.assertNotIn('foo_bar', pyglbuffers.LOADED_EXTENSIONS, 'Extension name is in the loaded extensions')
        self.assertFalse(extension_loaded('create_mmo'), 'Extension name is in the loaded extensions')
        self.assertFalse(extension_loaded('foo_bar'), 'Extension name is in the loaded extensions')
    
    def test_check(self):
        " Test extension support "
        self.assertFalse(check_extension('create_mmo'))        
        
if __name__ == '__main__':
    #Create an opengl context for our tests
    window = pyglet.window.Window(visible=False)
    unittest.main()