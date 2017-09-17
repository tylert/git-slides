#! /usr/bin/env python2
# -*- coding: utf-8; -*-

# apt-get install python-rsvg python-cairo python3-cairo


from argparse import ArgumentParser
from codecs import open
from xml.dom.minidom import parse

from cairo import Context, PDFSurface
from rsvg import Handle


NS_SVG = 'http://www.w3.org/2000/svg'
NS_INK = 'http://www.inkscape.org/namespaces/inkscape'
NS_JES = 'https://launchpad.net/jessyink'


if __name__ == '__main__':
    parser = ArgumentParser(description='Convert a JessyInk presentation')
    parser.add_argument('input', help='Input presentation')
    parser.add_argument('--output', dest='output', help='Output file')
    args = parser.parse_args()

    print args.input, args.output

    master = None
    slides = []

    # List all the slides and mark them as invisible
    dom = parse(args.input)
    for g in dom.getElementsByTagNameNS(NS_SVG, 'g'):
        if g.hasAttributeNS(NS_INK, 'groupmode') \
           and g.getAttributeNS(NS_INK, 'groupmode') == 'layer':
            if g.hasAttributeNS(NS_JES, 'masterSlide'):
                master = g
            else:
                slides.append(g)
                g.setAttributeNS(NS_SVG, 'visibility', 'hidden')

    # Fetch dimensions
    width = float(dom.documentElement.getAttribute('width'))
    height = float(dom.documentElement.getAttribute('height'))
    print '%f×%f' % (width, height)
    pdf = PDFSurface(args.output, width, height)
    cr = Context(pdf)

    # Display all the slides
    for i, s in enumerate(slides):
        slide_title = s.getAttributeNS(NS_INK, 'label')
        print 'Slide', (i+1), slide_title

        # Make the current slide visible
        s.setAttributeNS(NS_SVG, 'visibility', 'visible')
        s.setAttribute('style', 'display:inline')

        # Fill auto-texts
        for t in master.getElementsByTagNameNS(NS_SVG, 'tspan') \
                 + s.getElementsByTagNameNS(NS_SVG, 'tspan'):
            if t.hasAttributeNS(NS_JES, 'autoText'):
                txt = t.getAttributeNS(NS_JES, 'autoText')
                dat = t.childNodes[0]
                if txt == 'slideTitle':
                    dat.data = slide_title
                elif txt == 'slideNumber':
                    dat.data = '%d' % (i+1)
                elif txt == 'numberOfSlides':
                    dat.data = '%d' % len(slides)

        # Write the SVG XML code
        xml = dom.writexml(open('tmp.svg', 'w', 'utf-8'), encoding='utf-8')

        # Make the current slide hidden
        s.setAttributeNS(NS_SVG, 'visibility', 'hidden')
        s.setAttribute('style', 'display:none')

        # Render the SVG on a page
        fp = open(args.input)
        svg = Handle(file='tmp.svg')
        svg.render_cairo(cr)
        cr.show_page()
