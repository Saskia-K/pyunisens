# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 20:21:57 2019

A Python interface to the unisens data and container format http://www.unisens.org

Unisens is a universal data format for multi sensor data. 
It was developed at the FZI Research Center for Information Technology and 
the Institute for Information Processing Technology (ITIV) at the KIT 
(formerly University of Karlsruhe). The motivation for specifying a new data 
format was the need for a universal, generic and sustainable format for storing 
and archiving sensor data from various recording systems. Other main requirements 
were a human readable header and the use of future-proof standards like XML.


todo: summary
todo: plotting
todo: example file
todo: impolement del__
todo: implement update
todo: add group
todo: csvFileFormat standard
todo: add data
todo: channel to valuesentry
todo: parent in folder/parent
todo: access with shortcut to getitem
todo: removentry with shortcut / upper / lower
todo: coherent attribute setting in __init__ and set_data()

@author: skjerns
"""
import os
import logging
import datetime
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element
from .entry import Entry, FileEntry, ValuesEntry, SignalEntry, MiscEntry
from .entry import EventEntry, CustomEntry, CustomAttributes
from .utils import AttrDict, strip, validkey, lowercase, make_key, indent
  



    
class Unisens(Entry):
    """
    Initializes a Unisens object.
    If a unisens.xml file is already present in the folder, it will load
    the unisens data contained in this xml. If makenew=True is set, 
    the given unisens.xml will be replaced with a new unisens object.
    If no unisens.xml is present, a new unisens object will be created.
    
    :param folder: The folder where the unisens data is stored.
    :param makenew: Create a new unisens.xml, even if one is present.
                        If no unisens.xml is present and new=False
    :param attrib: The attribute 
    """
    def __init__(self, folder, makenew=False, autosave=False, readonly=False,
                 comment:str='', duration:int=0, measurementId:str='NaN', 
                 timestampStart='', filename='unisens.xml'):
        """
        Initializes a Unisens object.
        If a unisens.xml file is already present in the folder, it will load
        the unisens data contained in this xml. If makenew=True is set, 
        the given unisens.xml will be replaced with a new unisens object.
        If no unisens.xml is present, a new unisens object will be created.
        
        :param folder: The folder where the unisens data is stored.
        :param makenew: Create a new unisens.xml, even if one is present.
                        If no unisens.xml is present and new=False
        :param readonly: Select if any files should be written or not.
        :param attrib: The attribute 
        """
        assert autosave!=readonly or not autosave and not readonly, \
            'either read-only or autosave can be enabled'
        assert isinstance(folder, str), f'folder must be string, is {folder}'
        self._folder = folder
        self._file = os.path.join(folder, filename)
        os.makedirs(folder, exist_ok=True)
        folder = os.path.dirname(folder + '/')

        self.entries = AttrDict()
        self._entries = list()
        self._name = 'unisens'
        self._readonly = readonly
        
        if os.path.isfile(self._file) and not makenew:
            logging.info('loading unisens.xml from {}'.format(\
                         self._file))
            self.read_unisens(folder, filename=filename)
        else:
            logging.info('New unisens.xml will be created at {}'.format(\
                         self._file))
            if not timestampStart:
                now = datetime.datetime.now()
                timestampStart = now.strftime('%Y-%m-%dT%H:%M:%S')
            self.attrib  ={}
            self.set_attrib('comment', comment)
            self.set_attrib('duration', duration)
            self.set_attrib('measurementId', measurementId)
            self.set_attrib('timestampStart', timestampStart)
            self.set_attrib('version', '2.0')
            # self.set_attrib('xsi:schemaLocation',"http://www.unisens.org/unisens2.0"+\
            #               " http://www.unisens.org/unisens2.0/unisens.xsd")
            # self.set_attrib('xmlns',"http://www.unisens.org/unisens2.0")
            # self.set_attrib('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
        self._autosave_enabled = autosave
        self._autosave()
        
    def __setattr__(self, name, value):
        """
        This will allow to set new attributes with .attrname = value
        while warning the user if builtin methods are overwritten
        """
        return Entry.__setattr__(self, name, value)

   
    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except:
            return False   
        
    def __getitem__(self, key):
        if isinstance(key, str):
            # we don't care about case, gently ignoring Linux case-sensitivity
            for k in self.entries: 
                if k.upper()==key.upper():
                    return self.entries[k]
            # if this didn't work, we see if we find a unique 
            found = 0
            for k in self.entries:
                if os.path.splitext(k.upper())[0]==key.upper():
                    found+=1
                    fkey = k
            if found==1: return self.entries[fkey]
            if found>1: raise KeyError(f'Multiple keys start with {fkey}')
                
        elif isinstance(key, int):
            return self._entries[key]
        raise KeyError(f'{key} not found')
    
    def __str__(self):
        duration = self.__dict__.get('duration', 0)
        duration = str(datetime.timedelta(seconds=int(duration)))
        n_entries = len(self.entries) if hasattr(self, 'entries') else 0
        id = self.__dict__.get('measurementId', 'no ID')
        s = 'Unisens: {}({}, {} entries)'.format(id, duration, n_entries)
        return s
    
    def __repr__(self):
        comment = self.attrib.get('comment', '')
        comment = comment[:20] + '[..]'*(len(comment)>0)
        duration = self.attrib.get('duration', 0)
        duration = str(datetime.timedelta(seconds=int(duration)))
        measurementId = self.attrib.get('measurementId', 0)
        timestampStart = self.attrib.get('timestampStart', 0)

        s = f'Unisens(comment={comment}, duration={duration},  ' \
            f'id={measurementId},timestampStart={timestampStart})'
            
        return s
    
    
    def add_entry(self, entry:Entry):
        """
        Add a subentry to this unisens object, e.g ValueEntry, SignalEntry
        
        :param entry: An Entry subtype that should be added
        :returns: self
        """
        entry._folder = self._folder
        if isinstance(entry, FileEntry):
            if entry.id in self:            
                raise KeyError(f'{entry.id} already present in Unisens')
            self.entries[entry.id] = entry
        super().add_entry(entry, stack=False)
        return self
    
    
    def unpack_element(self, element:( Element, ET)) -> Entry:
        """
        Unpacks an xmltree element iteratively into an the
        corresponding subtype Entry object.
        
        :param element: An xml tree element
        """
        # iteratively upack_element the subelements of this element
        attrib = element.attrib.copy()
        entryType = strip(element.tag)
        if entryType == 'customAttributes':
            entry = CustomAttributes(attrib=attrib, parent=self._folder)
        elif entryType == 'eventEntry':
            entry = EventEntry(attrib=attrib, parent=self._folder, 
                               separator=';', decimalSeparator='.')
        elif entryType == 'signalEntry':
            entry = SignalEntry(attrib=attrib, parent=self._folder)
        elif entryType == 'valuesEntry':
            entry = ValuesEntry(attrib=attrib, parent=self._folder,
                                separator=';', decimalSeparator='.')
        elif entryType == 'customEntry':
            entry = CustomEntry(attrib=attrib, parent=self._folder)
        elif entryType in ('context', 'group', 'customAttribute', 
                           'csvFileFormat', 'channel', 'binFileFormat',
                           'customFileFormat', 'groupEntry'):
            name = element.tag
            entry = MiscEntry(name=name, attrib=attrib, parent=self._folder)
        else:
            if not 'Entry' in element.tag:
                logging.warning('Unknown entry type: {}'.format(entryType))
            name = element.tag
            entry = MiscEntry(name=name, attrib=attrib, parent=self._folder)
        for subelement in element:
            subentry = self.unpack_element(subelement)
            entry.add_entry(subentry)
        return entry
    
    def save(self, folder:str=None, filename:str='unisens.xml') -> Entry:
        """
        Save this Unisens xml file to a given folder and filename.
        filename should be unisens.xml, but can be altered if necessary
        
        :param folder: where to save the unisens description object.
                       will overwrite existing description file.
        :param filename: the filename to save. use unisens.xml.
        """
        self._check_readonly()
        
        if folder is None:
            folder = self._folder
        if filename is None:
            filename = os.path.basename(self._file)
            
        file = os.path.join(folder, filename)
        ET.register_namespace("", "http://www.unisens.org/unisens2.0")
        element = self.to_element()
        indent(element)
        et = ET.ElementTree(element)
        et.write(file, xml_declaration=True, default_namespace='', 
                 encoding='utf-8')
        return self
    
    
    def _autosave(self):
        
        if hasattr(self, '_autosave_enabled') and self._autosave_enabled:
            self.save()
            
            
    def read_unisens(self, folder:str, filename='unisens.xml') -> Entry:
        """
        Loads an XML Unisens file into this Unisens object.
        That means, self.attrib and self.children are added
        as well as tag, tail and text
        
        :param folder: folder where the unisens.xml is located. 
        :returns: self
        """
        folder += '/' # to avoid any ospath errors and confusion, append /
        file = os.path.join(os.path.dirname(folder), filename)
        if not os.path.exists(file):
            raise FileNotFoundError('{} does not exist'.format(folder))
            
        root = ET.parse(file).getroot()
        
        # copy all attributes from root to this Unisens object
        self.attrib = root.attrib
        # now add all elements that are contained in this XML object
        for element in root:
            entry = self.unpack_element(element)
            self.add_entry(entry)
            id = entry.attrib.get('id', entry._name)
            self.entries[id] = entry
        self.__dict__.update(self.attrib)
        keys = [make_key(key) for key in self.entries]
        entries = zip(keys, self.entries.values())
        self.__dict__.update(entries)
        return self


