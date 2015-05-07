
# coding: utf-8

# #Authoring VOEvent XML packets with ``voevent-parse``#

# In[ ]:

from __future__ import print_function
import voeventparse as vp
import datetime


# (To get started reading VOEvents, see the [previous notebook](01-parsing.ipynb)).
# 
# ##Packet creation##
# 
# We'll start by creating the skeleton of our VOEvent packet. We set the role to test so that nobody is tempted to start acting on the contents of this demo event. We also set the timestamp in the ``Who`` block to the time the event was generated (not when the observation was made), as per the 
# [specification](http://wiki.ivoa.net/twiki/bin/view/IVOA/VOEventTwoPointZero):

# In[ ]:

v = vp.Voevent(stream='hotwired.org/gaia_demo', stream_id=1,
                       role=vp.definitions.roles.test)


# In[ ]:

#Set Who.Date timestamp to date of packet-generation:
vp.set_who(v, date=datetime.datetime.utcnow(), 
        author_ivorn="foo.hotwired.hotwireduniverse.org/bar")
vp.set_author(v, title="Hotwired VOEvent Hands-on",
                      contactName="Joe Bloggs")
v.Description = "This is not an official Gaia data product."


# At any time, you can use ``vp.dumps`` (dump-string) to take a look at the VOEvent you've composed so far:

# In[ ]:

# print(vp.dumps(v, pretty_print=True))


# However, that's pretty dense! Use ``vp.prettystr`` to view a single element, which is a bit easier on the eyes:

# In[ ]:

print(vp.prettystr(v.Who))


# ##Adding ``What`` content##
# 
# We'll add details from this GAIA event:
# 
# | Name      | UTC timestamp       | RA        | Dec       | AlertMag | HistMag | HistStdDev | Class   | Comment                                                  | Published         |
# |-----------|---------------------|-----------|-----------|----------|---------|------------|---------|----------------------------------------------------------|-------------------|
# | Gaia14adi | 2014-11-07 01:05:09 | 168.47841 | -23.01221 | 18.77    | 19.62   | 0.07       | unknown | Fading source on top of 2MASS Galaxy (offset from bulge) | 2 Dec 2014, 13:55 |

# Now let's add details of the observation itself. We'll record both the magnitude that Gaia is reporting for this particular event, and the historic values they also provide:

# In[ ]:

v.What.append(vp.Param(name="mag", value=18.77, ucd="phot.mag"))
h_m = vp.Param(name="hist_mag", value=19.62, ucd="phot.mag")
h_s = vp.Param(name="hist_scatter", value=0.07, ucd="phot.mag")
v.What.append(vp.Group(params=[h_m, h_s], name="historic"))


# ##Adding ``WhereWhen`` details##
# Now we need to specify where and when the observation was made. Rather than trying to specify a position for Gaia, we'll just call it out by name. Note that Gaia don't provide errors on the position they cite, so we're rather optimistically using 0:

# In[ ]:

vp.add_where_when(v,
               coords=vp.Position2D(ra=168.47841, dec=-23.01221, err=0, units='deg',
                                    system=vp.definitions.sky_coord_system.fk5),
               obs_time=datetime.datetime(2014, 11, 7, 1, 5, 9),
               observatory_location="Gaia")


# In[ ]:

## See how much element creation that routine just saved us(!):
# print(vp.prettystr(v.WhereWhen))


# ##Adding the ``How``##
# We should also describe how this transient was detected, and refer to the name
# that Gaia have assigned it. Note that we can provide multiple descriptions
# (and/or references) here:

# In[ ]:

vp.add_how(v, descriptions=['Scraped from the Gaia website',
                                        'This is Gaia14adi'],
                       references=vp.Reference("http://gsaweb.ast.cam.ac.uk/alerts/"))


# ##And finally, ``Why``##
# Finally, we can provide some information about why this even might be scientifically interesting. Gaia haven't provided a classification, but we can at least incorporate the textual description:

# In[ ]:

vp.add_why(v)
v.Why.Description = "Fading source on top of 2MASS Galaxy (offset from bulge)"


# ##Check and save##
# Finally - and importantly, as discussed in the [VOEvent notes](http://voevent.readthedocs.org/en/latest/parse.html) - let's make sure that this event is really valid according to our schema:

# In[ ]:

vp.valid_as_v2_0(v)


# Great! We can now save it to disk:

# In[ ]:

with open('gaia.xml', 'w') as f:
                vp.dump(v, f)


# And we're all done. You can open the file in your favourite text editor to see what
# we've produced, but note that it probably won't be particularly elegantly
# formatted - an alternative option is to [open it in your browser](my_gaia.xml).

# ##Advanced##
# ###Free-style element authoring###
# Note that if you want to do something that's not part of the standard use-cases addressed by voevent-parse,
# you can always use the underlying lxml.objectify tools to manipulate elements yourself.
# For example - don't like the 'voevent-parse' tag that gets added to your VOEvent Who skeleton? You can delete it:

# In[ ]:

## Before deletion:
## (Enclosed in an if-clause in case this is re-run after the cell below)
if hasattr(v.Who, 'Description'): 
    print(v.Who.Description)


# In[ ]:

if hasattr(v.Who, 'Description'):
    del v.Who.Description
#Now it's gone!
print(vp.prettystr(v.Who))


# Want to add some additional elements of your own? 
# Here's how, but: make sure you stick to the VOEvent schema!

# In[ ]:

import lxml.objectify as objectify


# In[ ]:

# This won't last long:
vp.valid_as_v2_0(v)


# If you just want a single text-value element (with no siblings of the same name), you can take a syntactic shortcut and simply assign to it: 
# 
# *(Under the hood this assigns a new child ``StringElement`` to that tag - if there are pre-existing elements with that same tag, it is assigned to the first position in the list)*

# In[ ]:

v.What.shortcut='some text assigned in a quick-and-dirty fashion'
print (vp.prettystr(v.What))


# In general, though, you probably want to use [SubElement](http://lxml.de/objectify.html#the-lxml-objectify-api), 
# as this allows you to create multiple sibling-child elements of the same name, etc.

# In[ ]:

for i in range(5):
    objectify.SubElement(v.What, 'foo')
    v.What.foo[-1]="foo{}".format(i)
print("I have {} foos for you:".format(len(v.What.foo)))
print (vp.prettystr(v.What))


# In[ ]:

# Get rid of all the foo:
del v.What.foo[:]


# Alternatively, you can create elements independently, then append them to a parent (remember how lxml.objectify pretends elements are lists?) - this is occasionally useful if you want to write a function that returns an element, e.g. to create a new [Param](http://voevent-parse.readthedocs.org/en/master/reference.html#voeventparse.misc.Param) (but voevent-parse wraps that up for you already):

# In[ ]:

temp = objectify.Element('NonSchemaCompliantParam', attrib={'somekey':'somevalue'})
v.What.append(temp)
print(vp.prettystr(v.What))


# Obviously, these are non-schema compliant elements.
# Don't make up your own format - use Params for storing general data:

# In[ ]:

vp.valid_as_v2_0(v)


# Note that you can get a traceback if you need to figure out why a VOEvent is non-schema-compliant - this will report the first invalid element it comes across:

# In[ ]:

vp.assert_valid_as_v2_0(v)

