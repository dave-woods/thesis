this.initialState = {
    nextId: 1,
    eventStrings: [],
    ids: [],
    prevState: [],
    removed: null
}
this.state = {
    nextId: 1,
    eventStrings: [],
    ids: [],
    prevState: [],
    removed: null
}

function updateState(newState) {
    this.state.prevState = [{...this.state, prevState: null}, ...this.state.prevState.slice(0, 50)]
    this.state = {...this.state, removed: null, ...newState}
    updateDOM()
}

function resetState() {
    this.state = {
        ...this.initialState,
        removed: document.querySelector('.text pre').cloneNode(true),
        prevState: [{...this.state, prevState: null}, ...this.state.prevState.slice(0, 50)]
    }
    updateDOM()
}

function undo() {
    if (this.state.prevState.length === 0) return
    if (this.state.removed !== null) {
        document.querySelector('.text pre').replaceWith(this.state.removed)
    }
    const [cur, ...pre] = this.state.prevState
    this.state = cur
    this.state.prevState = pre
    updateDOM()
}

function getNextId(inserted) {
    let sortedIds = [inserted, ...this.state.ids].map(i => parseInt(i.substring(1)))
    sortedIds.sort((a, b) => a - b)
    return (sortedIds[sortedIds.length - 1] || this.state.nextId) + 1
}

function createMark(tag = 'EVENT') {
    if (window.getSelection) {
        const sel = window.getSelection()
        if (sel.type === 'Range' && sel.anchorNode === sel.focusNode && sel.anchorNode.parentElement === document.querySelector('.text pre') && sel.toString().trim() !== '') {
            if (sel.rangeCount) {
                const wrapEl = document.createElement('span')
                wrapEl.classList.add('tml-ev-ano', tag)
                if (tag === 'EVENT') {
                    wrapEl.dataset.id = `e${this.state.nextId}`
                    wrapEl.dataset.eventClass = 'OCCURRENCE'
                } else {
                    wrapEl.dataset.id = `t${this.state.nextId}`
                    wrapEl.dataset.type = 'DATE'
                }
                wrapEl.textContent = sel.toString()
                const range = sel.getRangeAt(0).cloneRange()
                range.deleteContents()
                range.insertNode(wrapEl)
                sel.removeAllRanges()
                sel.addRange(range)
                updateState({
                    nextId: getNextId(wrapEl.dataset.id),
                    // eventStrings: [...this.state.eventStrings, [`|${wrapEl.dataset.id}|`]],
                    ids: [...this.state.ids, wrapEl.dataset.id]
                })
            }
        }
    }
}

function removeMark(id) {
    const ev = document.querySelector(`[data-id="${id}"].tml-ev-ano`)
    const textNode = document.createTextNode(ev.textContent)
    const par = ev.parentElement
    const parClone = par.cloneNode(true)
    ev.replaceWith(textNode)
    par.normalize()
    return parClone
}

function updateEventList() {
    const eventListElem = document.querySelector('.event-list')
    const ev1Select = document.querySelector('.ev1')
    const ev2Select = document.querySelector('.ev2')
    eventListElem.textContent = ''
    ev1Select.textContent = ''
    ev2Select.textContent = ''

    for (id of this.state.ids) {
        const elem = document.querySelector(`[data-id="${id}"].tml-ev-ano`)
        if (!elem) { continue }

        const tag = elem.classList.contains('EVENT') ? 'EVENT' : 'TIMEX3'

        const eventListItem = document.createElement('li')

        const eventTagTextElem = document.createElement('span')
        eventTagTextElem.textContent = `${id}: ${elem.textContent}`

        const editMe = document.createElement('button')
        editMe.innerHTML = "&#43;"
        editMe.dataset.id = id
        editMe.addEventListener('click', e => {
            const edId = e.target.dataset.id
            toggleDisplayAddDetails(edId)
        })

        const removeMe = document.createElement('button')
        removeMe.innerHTML = "&times;"
        removeMe.dataset.id = id
        removeMe.addEventListener('click', e => {
            const remId = e.target.dataset.id
            const pc = removeMark(remId)
            updateState({
                eventStrings: this.state.eventStrings.filter(strs => !strs.includes(`|${remId}|`)),
                ids: this.state.ids.filter(i => i !== remId),
                removed: pc
            })
        })
        const eventButtons = document.createElement('div')
        eventButtons.style.display = 'flex'
        eventButtons.appendChild(editMe)
        eventButtons.appendChild(removeMe)

        eventListItem.appendChild(eventTagTextElem)
        eventListItem.appendChild(eventButtons)
        eventListElem.appendChild(eventListItem)

        const eventSelectItem = document.createElement('option')
        eventSelectItem.textContent = id
        eventSelectItem.value = id
        ev1Select.appendChild(eventSelectItem)
        ev2Select.appendChild(eventSelectItem.cloneNode(true))
    }

    document.querySelectorAll('span.tml-ev-ano').forEach(tagged => !this.state.ids.includes(tagged.dataset.id) && removeMark(tagged.dataset.id))
}

function updateStrings() {
    const eventStringsElem = document.querySelector('.strings')
    eventStringsElem.textContent = ''
    for (ev of this.state.eventStrings) {
        const eventStringItem = document.createElement('li')
        eventStringItem.textContent = `[${ev.join(', ')}]`
        eventStringsElem.prepend(eventStringItem)
    }
}

function addSuperpositionResults(results) {
    updateState({eventStrings: [...this.state.eventStrings, ...results]})
}

function updateDOM() {
    updateEventList()
    updateStrings()
    // console.log(this.state)
}

// for brython
function getStrings() {
    return this.state.eventStrings
}

function toggleDisplayHelp(setTo = null) {
    if (setTo === true) {
        document.querySelector('.help-wrap').classList.remove('hidden')
    } else if (setTo === false) {
        document.querySelector('.help-wrap').classList.add('hidden')
    } else {
        document.querySelector('.help-wrap').classList.toggle('hidden')
    }
}

function toggleDisplayAddDetails(id) {
    if (!id) {
        document.querySelector('.event-attr').classList.add('hidden')
        document.querySelector('.time-attr').classList.add('hidden')
        document.querySelector('.add-details-wrap').classList.add('hidden')
    } else {
        if (id.charAt(0) === 'e') {
            document.querySelector('.event-attr select').value = document.querySelector(`[data-id="${id}"].tml-ev-ano`).dataset.eventClass
            document.querySelector('.event-attr').classList.toggle('hidden')
        } else {
            document.querySelector('.time-attr').classList.toggle('hidden')
        }
        document.querySelector('.add-details').dataset.id = id
        document.querySelector('.add-details-wrap').classList.toggle('hidden')
    }
}

function exportTML() {
    const text = document.querySelector('.text pre').cloneNode(true)
    text.querySelectorAll('.EVENT').forEach(node => {
        node.replaceWith(document.createTextNode(`<EVENT eid="${node.dataset.id}">${node.textContent}</EVENT>`))
    })
    text.querySelectorAll('.TIMEX3').forEach(node => {
        node.replaceWith(document.createTextNode(`<TIMEX3 tid="${node.dataset.id}">${node.textContent}</TIMEX3>`))
    })
    return `<TimeML xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://timeml.org/timeMLdocs/TimeML_1.2.1.xsd">${text.textContent}</TimeML>`
}

function downloadTML() {
    const dlElem = document.createElement('a')

    dlElem.setAttribute('href', 'data:text/xml;charset=utf-8,' + encodeURIComponent(exportTML()))
    dlElem.setAttribute('download', 'export.tml')
    dlElem.style.display = 'none'

    document.body.appendChild(dlElem)
    dlElem.click()
    document.body.removeChild(dlElem)
}

function newAnnotation() {
    document.querySelector('.text').classList.add('hidden')
    document.querySelector('.input-text').classList.remove('hidden')
}

// Process the XML
const parseTML = (data) => {
    // Check the XML begins correctly
    if (!/^(<\?\s*xml version\s*=\s*"1.0"\s*\?>\s*)?<TimeML/.test(data)) {
        // alert(JSON.stringify({error: 'The file doesn\'t seem to be a valid TimeML file. Is it tagged correctly?'}, null, 2))
        return {
            imported: data
        }
    }
    // Initialise parser
    const parser = new window.DOMParser()
    const xml = parser.parseFromString(data, 'text/xml')
    const clone = xml.cloneNode(true)
    const pieces = []
    for (node of clone.firstChild.childNodes) {
        if (node.nodeName === 'EVENT') {
            const span = document.createElement('span')
            span.classList.add('tml-ev-ano', 'EVENT')
            span.textContent = node.textContent
            span.dataset.eventClass = node.attributes['class'].value
            span.dataset.id = node.attributes['eid'].value
            updateState({
                nextId: getNextId(span.dataset.id),
                // eventStrings: [...this.state.eventStrings, [`|${span.dataset.id}|`]],
                ids: [...this.state.ids, span.dataset.id]
            })
            pieces.push(span.outerHTML)
        } else if (node.nodeName === 'TIMEX3') {
            const span = document.createElement('span')
            span.classList.add('tml-ev-ano', 'TIMEX3')
            span.textContent = node.textContent
            span.dataset.type = node.attributes['type'].value
            span.dataset.functionInDocument = node.attributes['functionInDocument']?.value ?? 'NONE'
            span.dataset.value = node.attributes['value']?.value
            span.dataset.id = node.attributes['tid'].value
            updateState({
                nextId: getNextId(span.dataset.id),
                // eventStrings: [...this.state.eventStrings, [`|${span.dataset.id}|`]],
                ids: [...this.state.ids, span.dataset.id]
            })
            pieces.push(span.outerHTML)
        } else {
            pieces.push(node.textContent)
        }
    }
    
    const tlinks = xml.getElementsByTagName('TLINK')
    const lz = document.getElementById('lz')
    
    for (tlink of tlinks) {
        const { eventInstanceID, timeID, relatedToEventInstance, relatedToTime, relType } = tlink.attributes
        const rel = tmlToAllen[relType.value]
        const e1 = (eventInstanceID ?? timeID).value
        const e2 = (relatedToEventInstance ?? relatedToTime).value
        lz.value = `${e1},${rel},${e2}`
        lz.dispatchEvent(new InputEvent('change'))
    }
    // const stats = mapped.reduce((acc, tl) => {
    //     const ei = tl.eventInstanceID
    //     const rei = tl.relatedToEventInstance
    //     const t = tl.timeID
    //     const rt = tl.relatedToTime
    //     // Calculate frequencies of fluents
    //     const updateAcc = (a, l, x) => {
    //     if (a[l][x]) {
    //         a[l][x] += 1
    //     } else {
    //         a[l][x] = 1
    //     }
    //     if (!a.mostFrequent || (a[l][x] > a.mostFrequent.count)) {
    //         a.mostFrequent = {
    //         id: x,
    //         count: a[l][x]
    //         }
    //     }
    //     }
    //     if (ei) {
    //     updateAcc(acc, 'eventInstanceIDs', ei)
    //     } else if (t) {
    //     updateAcc(acc, 'timeIDs', t)
    //     }
    //     if (rei) {
    //     updateAcc(acc, 'eventInstanceIDs', rei)
    //     } else if (rt) {
    //     updateAcc(acc, 'timeIDs', rt)
    //     }
    //     return acc
    // }, {timeIDs: {}, eventInstanceIDs: {}})
    // // All fluents, regardless of type
    // const fluents = [...Object.keys(stats.timeIDs), ...Object.keys(stats.eventInstanceIDs)]
    // const fluentCount = fluents.length
    return {
        // length: mapped.length,
        // tlinks: mapped,
        // strs: mapped.map(tl => tl.str),
        // estrs: mapped.map(tl => tl.estr),
        // stats: Object.assign({}, {fluentCount, fluents}, {timeCounts: stats.timeIDs, eventInstanceCounts: stats.eventInstanceIDs, mostLinkedFluent: stats.mostFrequent}),
        imported: data,
        transformed: pieces.join(''),
        text: xml.documentElement.textContent.trim()
    }
}

const tmlToAllen = {
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

document.addEventListener('keyup', e => {
    const kb = e.key.toLowerCase()
    if (kb === 'e') {
        createMark('EVENT')
    } else if (kb === 't') {
        createMark('TIMEX3')
    } else if (kb === 'u') {
        undo()
    } else if (kb === '?') {
        toggleDisplayHelp()
    } else if (kb === 'escape') {
        toggleDisplayHelp(false)
        toggleDisplayAddDetails()
    }
    // else {console.log(kb)}
})
document.querySelector('.help-wrap').addEventListener('click', e => {
    e.stopPropagation()
    if (e.currentTarget === e.target) {
        toggleDisplayHelp()
    }
})
document.querySelector('.add-details-wrap').addEventListener('click', e => {
    e.stopPropagation()
    if (e.currentTarget === e.target) {
        toggleDisplayAddDetails()
    }
})
document.querySelector('.input-text button').addEventListener('click', () => {
    if (document.querySelector('.input-text textarea').value.trim() === '') return
    updateState({...this.initialState})
    const tml = parseTML(document.querySelector('.input-text textarea').value)
    if (tml.transformed) {
        document.querySelector('.text pre').innerHTML = tml.transformed.trim()
    } else {
        document.querySelector('.text pre').innerHTML = tml.imported.trim()
    }
    document.querySelector('.text').classList.remove('hidden')
    document.querySelector('.input-text').classList.add('hidden')
    updateState({prevState: []})
})
document.getElementById('btn-undo').addEventListener('click', undo.bind(this))
document.getElementById('btn-reset').addEventListener('click', resetState.bind(this))
document.getElementById('btn-tag-event').addEventListener('click', () => createMark('EVENT'))
document.getElementById('btn-tag-time').addEventListener('click', () => createMark('TIMEX3'))
document.getElementById('btn-help').addEventListener('click', () => toggleDisplayHelp(true))
document.getElementById('btn-export').addEventListener('click', downloadTML)
document.getElementById('btn-new').addEventListener('click', newAnnotation)
document.querySelector('.event-attr .update-attr').addEventListener('click', () => {
    const id = document.querySelector('.add-details').dataset.id
    document.querySelector(`[data-id="${id}"].tml-ev-ano`).dataset.eventClass = document.querySelector('.event-attr select').value
})
