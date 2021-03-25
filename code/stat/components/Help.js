export default function Help(props) {
  return (
    <div className="help-wrap" onClick={props.dismiss}>
        <div className="help">
          <h3>TimeML Annotation</h3>
          <p>
            Use the mouse to highlight text, then press 'Tag Event' to tag that text as an event, or press 'Tag Time' to tag that text as a time. Tagged events and times will appear in the upper right panel, where they may be removed or their attributes may be edited.
          </p>
          <p>
            Test or create relations from the tagged events and times in the lower left panel. Created relations will appear as strings in the String Bank. The string that will appear can be previewed to the right of the relation name when selecting a relation.
          </p>
          <p>
            The String Bank contains all of the known temporal relations, as strings. Triggering a superposition will attempt to consolidate this knowledge into a smaller number of strings by combining the data where it is sensible to do so, i.e. |a|b| + |b|c| = |a|b|c|. Since some superpositions may produce multiple strings as a result, the program will attempt to limit the resulting set to no more than <input style={{width: '6ch'}} type="number" min="0" max="99" defaultValue={props.limit} onChange={e => props.setLimit(parseInt(e.currentTarget.value))}/> strings (use 0 for no limit - this may be slow and produce unwieldy results). Clicking Superpose iteratively may consolidate the results further.
          </p>
          <p>
            Clicking Export will export the annotated text as a TimeML file.
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
        </div>
      </div>
  )
}
