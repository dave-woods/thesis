import { useState } from 'react'
import { getFreksa } from '../fns/getFreksa'

export default function CreateRelation(props) {
  const [ev1, setEv1] = useState('')
  const [ev2, setEv2] = useState('')
  const [rel, setRel] = useState('')

  const addNewRelation = async () => {
    getFreksa(ev1, ev2, rel).then(resp => resp.json()).then(data => {
      props.addRelation(JSON.parse(data.stdout))
    })
  }

  return (
    <div className="relations">
      <div>
        <select defaultValue={''} className="ev1" onChange={e => setEv1(e.currentTarget.value)}>
          {ev1 === '' && <option disabled value=''></option>}
          {props.events.map(ev => <option key={`ev1-${ev.id}`} value={ev.id}>{ev.id}</option>)}
        </select> is <select defaultValue={''} className="rel" onChange={e => setRel(e.currentTarget.value)} disabled={ev1 === ev2}>
          {rel === '' && <option disabled value=''></option>}
          <option value="b">BEFORE (|{ev1}||{ev2}|)</option>
          <option value="bi">AFTER (|{ev2}||{ev1}|)</option>
          <option value="m">MEETING (|{ev1}|{ev2}|)</option>
          <option value="mi">MET BY (|{ev2}|{ev1}|)</option>
          <option value="s">STARTING (|{ev1},{ev2}|{ev2}|)</option>
          <option value="si">STARTED BY (|{ev1},{ev2}|{ev1}|)</option>
          <option value="f">FINISHING (|{ev2}|{ev1},{ev2}|)</option>
          <option value="fi">FINISHED BY (|{ev1}|{ev1},{ev2}|)</option>
          <option value="di">CONTAINING (|{ev1}|{ev1},{ev2}|{ev1}|)</option>
          <option value="d">CONTAINED BY (|{ev2}|{ev1},{ev2}|{ev2}|)</option>
          <option value="o">OVERLAPPING (|{ev1}|{ev1},{ev2}|{ev2}|)</option>
          <option value="oi">OVERLAPPED BY (|{ev2}|{ev1},{ev2}|{ev1}|)</option>
          <option value="e">EQUAL TO (|{ev1},{ev2}|)</option>
        </select> <select defaultValue={''} className="ev2" onChange={e => setEv2(e.currentTarget.value)}>
          {ev2 === '' && <option disabled value=''></option>}
          {props.events.map(ev => <option key={`ev2-${ev.id}`} value={ev.id}>{ev.id}</option>)}
        </select>
      </div>
      <button id="createRelation" disabled={ev1 === ev2 || ev1 === '' || ev2 === '' || rel === ''} onClick={addNewRelation}>Add New Relation</button>
      <button id="testRelation" disabled={ev1 === ev2 || ev1 === '' || ev2 === '' || rel === ''} onClick={() => props.testRelation(ev1, ev2, rel)}>Test Relation</button>
    </div>
  )
}
