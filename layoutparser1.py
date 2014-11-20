#!/usr/bin/env python

# parse an xml layout and produce android code to access the elements with ids

import sys
import os
import xml.parsers.expat

privates = str()
lookups = str()

if len(sys.argv) < 2:
    print "Usage " , sys.argv[0] , " layout.xml";
else:
    baseLayoutStr = sys.argv[2] if len(sys.argv)>2 else "baseLayout"
    
    def getCamelCase(rid):
        rname = ''
        foundunderscore = False
        for i, c in enumerate(rid):
            if c == '_':
                if i == 0:
                    return
                foundunderscore = True
                i += 1
            elif foundunderscore:
                rname += c.upper()
                foundunderscore = False
            else:
                rname += c
        return rname

    
    adapter = False
    if len(sys.argv) == 4:
        adapter = True

    def get_start_element_handler(layout_base_name="baseLayout"):    
        def start_element(name, attrs):
            global privates
            global lookups
            global p
            if 'android:id' in attrs:
                oclassname = classname = str(name)
                if classname == 'include' or classname == 'merge':
                    classname = 'View'
                    

                
                dotindex = classname.rfind('.')
                if dotindex != -1:
                    classname = classname[dotindex+1:]
                rid = str(attrs.get('android:id'))
                rid = rid[rid.find('/')+1:]
                rname = getCamelCase(rid)
                privates += '' if adapter else ' '
                rnewname = getCamelCase(rname if layout_base_name=="baseLayout" else layout_base_name+"_"+rname)
                privates += classname + ' ' +  rnewname + ';\n'
                lookups += 'holder.' if adapter else '' 
                lookups += rnewname + ' = (' + classname + ') '
                lookups += 'convertView.' if adapter else ''
                lookups += layout_base_name+'.findViewById(R.id.' + rid + ');\n'
                if classname == 'Button':
                    lookups += 'holder.' if adapter else '' 
                    lookups += rname + '.setOnClickListener(new View.OnClickListener() {\n'
                    lookups += '\t@Override\n'
                    lookups += '\tpublic void onClick(View v) {\n'
                    lookups += '\t\t' + rname + 'Clicked();\n'
                    lookups += '\t}\n'
                    lookups += '});\n'
                if(oclassname=="include"):
                    p1 = xml.parsers.expat.ParserCreate()
                    rid = str(attrs.get('android:id'))
                    rid = rid[rid.find('/')+1:]
                    p1.StartElementHandler = get_start_element_handler(layout_base_name = getCamelCase(rid))
                    p1.ParseFile(open(os.path.split(sys.argv[1])[0]+"/"+attrs["layout"].split("/")[-1]+".xml","r"))


                #print 'Start element:', name, "attrs:", attrs
                #print 'rid', rid
                #print 'rname', rname
        return start_element    


    p = xml.parsers.expat.ParserCreate()
    p.StartElementHandler = get_start_element_handler(baseLayoutStr)

    f = open(sys.argv[1],"r");
    p.ParseFile(f)

    print privates
    print lookups
