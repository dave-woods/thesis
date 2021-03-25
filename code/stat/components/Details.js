import { useState, useEffect, useRef } from 'react'

export default function Details(props) {
  const [attribs, setAttribs] = useState({...props.event.attr})
  const detailsRef = useRef(null)
  useEffect(() => {
    detailsRef.current && detailsRef.current.focus()
  }, [])

  return (
    <div className="add-details-wrap" onClick={props.dismiss}>
      <div className="add-details">
        <h2>{props.event.id}: {props.event.text}</h2>
        <h3>Edit attributes</h3>
        {props.event.type === 'EVENT' ? <ul className="attr-list">
          <li>
            <label htmlFor="class-select">Class:</label> <select ref={detailsRef} id="class-select" defaultValue={attribs.class} onChange={e => setAttribs(prev => ({...prev, class: e.target.value}))}>
              <option value="OCCURRENCE">OCCURRENCE</option>
              <option value="PERCEPTION">PERCEPTION</option>
              <option value="REPORTING">REPORTING</option>
              <option value="ASPECTUAL">ASPECTUAL</option>
              <option value="STATE">STATE</option>
              <option value="I_STATE">I_STATE</option>
              <option value="I_ACTION">I_ACTION</option>
            </select>
          </li>
          <li>
            <label htmlFor="tense-select">Tense:</label> <select id="tense-select" defaultValue={attribs.tense} onChange={e => setAttribs(prev => ({...prev, tense: e.target.value}))}>
              <option value="NONE">NONE</option>
              <option value="PAST">PAST</option>
              <option value="PRESENT">PRESENT</option>
              <option value="FUTURE">FUTURE</option>
            </select>
          </li>
          <li>
            <label htmlFor="aspect-select">Aspect:</label> <select id="aspect-select" defaultValue={attribs.aspect} onChange={e => setAttribs(prev => ({...prev, aspect: e.target.value}))}>
              <option value="NONE">NONE</option>
              <option value="PROGRESSIVE">PROGRESSIVE</option>
              <option value="PERFECTIVE">PERFECTIVE</option>
              <option value="PERFECTIVE_PROGRESSIVE">PERFECTIVE_PROGRESSIVE</option>
            </select>
          </li>
          <li>
            <label htmlFor="polarity-select">Polarity:</label> <select id="polarity-select" defaultValue={attribs.polarity} onChange={e => setAttribs(prev => ({...prev, polarity: e.target.value}))}>
              <option value="POS">POS</option>
              <option value="NEG">NEG</option>
            </select>
          </li>
        </ul>
        :
        <ul className="attr-list">
          <li>
            <label htmlFor="type-select">Type:</label> <select ref={detailsRef} id="type-select" defaultValue={attribs.type} onChange={e => setAttribs(prev => ({...prev, type: e.target.value}))}>
              <option value="DATE">DATE</option>
              <option value="TIME">TIME</option>
              <option value="DURATION">DURATION</option>
              <option value="SET">SET</option>
            </select>
          </li>
          <li>
            <label htmlFor="function-in-doc-select">Function in doc:</label> <select id="function-in-doc-select" defaultValue={attribs.functionInDocument} onChange={e => setAttribs(prev => ({...prev, functionInDocument: e.target.value}))}>
              <option value="NONE">NONE</option>
              <option value="CREATION_TIME">CREATION_TIME</option>
              <option value="EXPIRATION_TIME">EXPIRATION_TIME</option>
              <option value="MODIFICATION_TIME">MODIFICATION_TIME</option>
              <option value="PUBLICATION_TIME">PUBLICATION_TIME</option>
              <option value="RELEASE_TIME">RELEASE_TIME</option>
              <option value="RECEPTION_TIME">RECEPTION_TIME</option>
            </select>
          </li>
          <li>
            <label htmlFor="temporal-func-select">Temporal function:</label> <select id="temporal-func-select" defaultValue={attribs.temporalFunction} onChange={e => setAttribs(prev => ({...prev, temporalFunction: e.target.value}))}>
              <option value="false">false</option>
              <option value="true">true</option>
            </select>
          </li>
          <li>
            <label htmlFor="value-input">Value:</label> <input id="value-input" defaultValue={attribs.value} onChange={e => setAttribs(prev => ({...prev, value: e.target.value}))}/>
          </li>
          <li>
            <label htmlFor="anchor-time-input">Anchor time ID:</label> <input id="anchor-time-input" defaultValue={attribs.anchorTimeID} onChange={e => setAttribs(prev => ({...prev, anchorTimeID: e.target.value}))}/>
          </li>
        </ul>
        }
        <button className="update-attr" onClick={e => {
          props.update(props.event.id, attribs)
          props.dismiss(e)
        }}>Update</button>
      </div>
    </div>
  )
}
