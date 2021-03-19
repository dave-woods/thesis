export const parseTML = inputString => {
    const parser = new window.DOMParser()
    const xml = parser.parseFromString(inputString, 'text/xml')
    
    if (xml.documentElement.nodeName == "parsererror" || xml.documentElement.getElementsByTagName('parsererror').length > 0) {
      return {
        imported: inputString
      }
    }

    const pieces = []
    const events = []
    // const events = []
    // const timexs = []
    for (let node of xml.firstChild.childNodes) {
        if (node.nodeName === 'EVENT') {
            const span = document.createElement('span')
            span.classList.add('tml-ev-ano', 'EVENT')
            span.textContent = node.textContent
            span.dataset.eventClass = node.attributes['class'].value
            span.dataset.id = node.attributes['eid'].value
            // ids.push(span.dataset.id)
            events.push({
              id: span.dataset.id,
              type: 'EVENT',
              text: span.textContent,
              attr: node.attributes
            })
            // updateState({
                // nextId: getNextId(span.dataset.id),
                // eventStrings: [...this.state.eventStrings, [`|${span.dataset.id}|`]],
                // ids: [...this.state.ids, span.dataset.id]
            // })
            pieces.push(span.outerHTML)
        } else if (node.nodeName === 'TIMEX3') {
            const span = document.createElement('span')
            span.classList.add('tml-ev-ano', 'TIMEX3')
            span.textContent = node.textContent
            span.dataset.type = node.attributes['type'].value
            span.dataset.functionInDocument = node.attributes['functionInDocument']?.value ?? 'NONE'
            span.dataset.value = node.attributes['value']?.value
            span.dataset.id = node.attributes['tid'].value
            // ids.push(span.dataset.id)
            events.push({
              id: span.dataset.id,
              type: 'TIMEX3',
              text: span.textContent,
              attr: node.attributes
            })
            // updateState({
                // nextId: getNextId(span.dataset.id),
                // eventStrings: [...this.state.eventStrings, [`|${span.dataset.id}|`]],
                // ids: [...this.state.ids, span.dataset.id]
            // })
            pieces.push(span.outerHTML)
        } else {
            pieces.push(node.textContent)
        }
    }
    
    const tlinks = [...xml.getElementsByTagName('TLINK')].map(tlink => {
      const { eventInstanceID, timeID, relatedToEventInstance, relatedToTime, relType } = tlink.attributes
      return {
        rel: tmlToAllen[relType.value],
        e1: (eventInstanceID ?? timeID).value,
        e2: (relatedToEventInstance ?? relatedToTime).value
      }
    })
    return {
        imported: inputString,
        transformed: pieces.join('').trim(),
        text: xml.documentElement.textContent.trim(),
        events,
        // timexs,
        // ids,
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
