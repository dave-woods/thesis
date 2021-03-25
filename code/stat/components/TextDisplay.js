import { useRef } from 'react'

export default function TextDisplay(props) {
  const elem = useRef(null)

  function exportTML() {
    const newText = elem.current.cloneNode(true)
    newText.querySelectorAll('.EVENT').forEach(node => {
        node.replaceWith(document.createTextNode(`<EVENT eid="${node.dataset.id}">${node.textContent}</EVENT>`))
    })
    newText.querySelectorAll('.TIMEX3').forEach(node => {
        node.replaceWith(document.createTextNode(`<TIMEX3 tid="${node.dataset.id}">${node.textContent}</TIMEX3>`))
    })
    return `<TimeML xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://timeml.org/timeMLdocs/TimeML_1.2.1.xsd">${newText.textContent}</TimeML>`
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

  return (
    <div className="text">
      <pre dangerouslySetInnerHTML={{ __html: props.text}} ref={elem}></pre>
      <div className="btns">
        <button id="btn-new" onClick={props.reset}>New</button>
        <button id="btn-export" onClick={() => props.download(elem)}>Export</button>
      </div>
    </div>
  )
}
