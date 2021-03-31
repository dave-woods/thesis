export const parseTML = inputString => {
    const parser = new window.DOMParser()
    const xml = parser.parseFromString(inputString.trim(), 'text/xml')
    
    if (xml.documentElement.nodeName == "parsererror" || xml.documentElement.getElementsByTagName('parsererror').length > 0) {
      return {
        imported: inputString
      }
    }
    let nodes = []
    if (xml.firstChild.getElementsByTagName('TEXT').length === 0) {
      nodes = xml.firstChild.childNodes
    } else {
      nodes = [...xml.firstChild.getElementsByTagName('DCT')[0].childNodes, ...xml.firstChild.getElementsByTagName('TEXT')[0].childNodes]
    }

    const instances = [...xml.getElementsByTagName('MAKEINSTANCE')].map(mi => {
      const {eventID, eiid, ...rest} = Object.assign({}, ...Array.from(mi.attributes, ({name, value}) => ({[name]: value})));
      return {
        eventID,
        eiid,
        rest
      }
    })

    const pieces = []
    const events = []
    for (let node of nodes) {
        if (node.nodeName === 'EVENT') {
            const nodeAttr = Object.assign({}, ...Array.from(node.attributes, ({name, value}) => ({[name]: value})));
            const span = document.createElement('span')
            span.classList.add('tml-ev-ano', 'EVENT')
            span.textContent = node.textContent
            const {eid, ...nodeRest} = nodeAttr
            span.dataset.id = eid
            const inst = instances.find(i => i.eventID === eid)
            events.push({
              id: eid,
              type: 'EVENT',
              text: span.textContent,
              elem: span,
              attr: {...nodeRest, ...inst.rest}
            })
            pieces.push(span.outerHTML)
        } else if (node.nodeName === 'TIMEX3') {
            const nodeAttr = Object.assign({}, ...Array.from(node.attributes, ({name, value}) => ({[name]: value})));
            const span = document.createElement('span')
            span.classList.add('tml-ev-ano', 'TIMEX3')
            span.textContent = node.textContent
            const {tid, ...nodeRest} = nodeAttr
            span.dataset.id = tid
            events.push({
              id: tid,
              type: 'TIMEX3',
              text: span.textContent,
              elem: span,
              attr: {...nodeRest} 
            })
            pieces.push(span.outerHTML)
        } else {
            pieces.push(node.textContent)
        }
    }
    
    const tlinks = [...xml.getElementsByTagName('TLINK')].map(tlink => {
      const { eventInstanceID, timeID, relatedToEventInstance, relatedToTime, relType } = tlink.attributes
      const e1 = instances.find(i => eventInstanceID !== undefined && i.eiid === eventInstanceID.value)?.eventID ?? timeID.value
      const e2 = instances.find(i => relatedToEventInstance !== undefined && i.eiid === relatedToEventInstance.value)?.eventID ?? relatedToTime.value
      return {
        rel: tmlToAllen[relType.value],
        e1,
        e2,
        warning: e1 === e2
      }
    })
    return {
        imported: inputString,
        transformed: pieces.join('').trim(),
        text: xml.documentElement.textContent.trim(),
        events,
        tlinks
    }
}

export const tmlToAllen = {
    BEFORE: 'b',
    AFTER: 'bi',
    INCLUDES: 'di',
    DURING_INV: 'di',
    IS_INCLUDED: 'd',
    DURING: 'd',
    SIMULTANEOUS: 'e',
    IDENTITY: 'e',
    IAFTER: 'mi',
    IBEFORE: 'm',
    BEGINS: 's',
    ENDS: 'f',
    BEGUN_BY: 'si',
    ENDED_BY: 'fi'
}
