import { useState } from 'react'
import * as freksa from '../fns/freksa'

export default function CreateRelation(props) {
  const [ev1, setEv1] = useState('')
  const [ev2, setEv2] = useState('')
  const [rel, setRel] = useState('')

  const addNewRelation = () => {
    props.addRelation(freksa[rel](ev1, ev2))
  }

  return (
    <div className="relations">
      <ul>
        <li>
        <label htmlFor="ev1-select">Event 1:</label> <select id="ev1-select" defaultValue={''} className="ev1" onChange={e => setEv1(e.currentTarget.value)}>
          {ev1 === '' && <option disabled value=''>Select Event</option>}
          {props.events.map(ev => <option key={`ev1-${ev.id}`} value={ev.id}>{ev.id}</option>)}
        </select>
        </li>
        <li>
        <label htmlFor="rel-select">Rel:</label> <select defaultValue={''} className="rel" onChange={e => setRel(e.currentTarget.value)} disabled={ev1 === ev2 || ev1 === '' || ev2 === ''}>
          {rel === '' && <option disabled value=''>Select Relation</option>}
          <option value="b">BEFORE (|{ev1}||{ev2}|)</option>
          <option value="bi">AFTER (|{ev2}||{ev1}|)</option>
          <option value="m">IBEFORE (|{ev1}|{ev2}|)</option>
          {/* <option value="m">MEETING (|{ev1}|{ev2}|)</option> */}
          <option value="mi">IAFTER (|{ev2}|{ev1}|)</option>
          {/* <option value="mi">MET BY (|{ev2}|{ev1}|)</option> */}
          <option value="s">BEGINS (|{ev1},{ev2}|{ev2}|)</option>
          {/* <option value="s">STARTING (|{ev1},{ev2}|{ev2}|)</option> */}
          <option value="si">BEGUN_BY (|{ev1},{ev2}|{ev1}|)</option>
          {/* <option value="si">STARTED BY (|{ev1},{ev2}|{ev1}|)</option> */}
          <option value="f">ENDS (|{ev2}|{ev1},{ev2}|)</option>
          {/* <option value="f">FINISHING (|{ev2}|{ev1},{ev2}|)</option> */}
          <option value="fi">ENDED_BY (|{ev1}|{ev1},{ev2}|)</option>
          {/* <option value="fi">FINISHED BY (|{ev1}|{ev1},{ev2}|)</option> */}
          <option value="di">INCLUDES (|{ev1}|{ev1},{ev2}|{ev1}|)</option>
          {/* <option value="di">CONTAINING (|{ev1}|{ev1},{ev2}|{ev1}|)</option> */}
          <option value="d">DURING (|{ev2}|{ev1},{ev2}|{ev2}|)</option>
          {/* <option value="d">CONTAINED BY (|{ev2}|{ev1},{ev2}|{ev2}|)</option> */}
          {/* <option value="o">OVERLAPPING (|{ev1}|{ev1},{ev2}|{ev2}|)</option> */}
          {/* <option value="oi">OVERLAPPED BY (|{ev2}|{ev1},{ev2}|{ev1}|)</option> */}
          <option value="e">SIMULTANEOUS (|{ev1},{ev2}|)</option>
        </select>
        </li>
        <li>
        <label htmlFor="ev2-select">Event 2:</label> <select defaultValue={''} className="ev2" onChange={e => setEv2(e.currentTarget.value)}>
          {ev2 === '' && <option disabled value=''>Select Event</option>}
          {props.events.map(ev => <option key={`ev2-${ev.id}`} value={ev.id}>{ev.id}</option>)}
        </select>
        </li>
      </ul>
      <button id="testRelation" disabled={ev1 === ev2 || ev1 === '' || ev2 === '' || rel === ''} onClick={() => props.testRelation(ev1, ev2, rel)}>Test Relation</button>
      <button id="createRelation" disabled={ev1 === ev2 || ev1 === '' || ev2 === '' || rel === ''} onClick={addNewRelation}>Add New Relation</button>
    </div>
  )
}
