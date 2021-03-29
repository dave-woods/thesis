import { useState } from 'react'

export default function Help(props) {
  const [page, setPage] = useState(1)

  return (
    <div className="overlay" onClick={props.dismiss}>
        <div className="help">
          <h3>START (String Temporal Annotation and Relation Tool)</h3>
          {page === 1 && <div id="help-p1">
            <p>
              Use the mouse to highlight text, then press 'Tag Event' to tag that text as an event, or press 'Tag Time' to tag that text as a time. Tagged events and times will appear in the upper right panel, where they may be removed or their attributes may be edited.
            </p>
            <p>
              Keyboard shortcuts:
            </p>
            <ul>
              <li>E: Tag Event</li>
              <li>T: Tag Time</li>
              <li>U: Undo</li>
              <li>S: Superpose</li>
              <li>?: Toggle Help</li>
            </ul>
            <a style={{cursor: 'pointer', float: 'right'}} onClick={() => setPage(2)}>More</a>
          </div>}
          {page === 2 && <div id="help-p2">
            <p>
              Test or create relations from the tagged events and times in the lower left panel. Created relations will appear as strings in the String Bank. The string that will appear can be previewed to the right of the relation name when selecting a relation. You can also try to find the relations between a pair of temporal entities that are currently present in the String Bank.
            </p>
            <p>
              Check this box to allow Freksa relation input (these will not appear in the exported TimeML, click <a target="_blank" rel="noopener noreferrer" href="/freksa.html">here for more info</a>): <input type="checkbox" checked={props.extendedRels} onChange={e => props.setExtendedRels(e.currentTarget.checked)} />
            </p>
            <p>
              The String Bank contains all of the known temporal relations, as strings. Triggering a superposition will attempt to consolidate this knowledge into a smaller number of strings by combining the data where it is sensible to do so, i.e. |a|b| + |b|c| = |a|b|c|. Since some superpositions may produce multiple strings as a result, the program will attempt to limit the resulting set to no more than <input style={{width: '6ch'}} type="number" min="0" max="99" defaultValue={props.limit} onChange={e => props.setLimit(parseInt(e.currentTarget.value))}/> strings (use 0 for no limit - this may be slow and produce unwieldy results). Clicking on a string will show the <code>{`<TLINK>`}</code> tags derivable from it.
            </p>
            <a style={{cursor: 'pointer', float: 'left'}} onClick={() => setPage(1)}>Back</a>
            <a style={{cursor: 'pointer', float: 'right'}} onClick={() => setPage(3)}>More</a>
          </div>}
          {page === 3 && <div id="help-p3">
            <p>
              Clicking Export will export the annotated text as a TimeML (v1.2) file. Note that <code>{`<MAKEINSTANCE>`}</code> tags are not output, and their attributes are shifted to the <code>{`<EVENT>`}</code> tags. <code>{`<TLINK>`}</code> tags use eventIDs instead of eventInstanceIDs, and the relType may include a disjunction of relations if multiple options were derivable from the String bank, e.g. relType="BEFORE|IBEFORE". The OVERLAPS and OVERLAPPED_BY relations are also permitted in the output if they are derived.
            </p>
            <a style={{cursor: 'pointer', float: 'left'}} onClick={() => setPage(2)}>Back</a>
          </div>}
        </div>
      </div>
  )
}
