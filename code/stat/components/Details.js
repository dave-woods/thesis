export default function Details(props) {
  return (
    <div className="add-details-wrap" onClick={props.dismiss}>
      <div className="add-details">
        <h3>Add attributes</h3>
        <div className="event-attr">
          Class: <select>
            <option value="OCCURRENCE">OCCURRENCE</option>
            <option value="PERCEPTION">PERCEPTION</option>
            <option value="REPORTING">REPORTING</option>
            <option value="ASPECTUAL">ASPECTUAL</option>
            <option value="STATE">STATE</option>
            <option value="I_STATE">I_STATE</option>
            <option value="I_ACTION">I_ACTION</option>
          </select>
          <button className="update-attr">Update</button>
        </div>
        <div className="time-attr">
          Type: <select>
            <option value="DATE">DATE</option>
            <option value="TIME">TIME</option>
            <option value="DURATION">DURATION</option>
            <option value="SET">SET</option>
          </select>
          <button className="update-attr">Update</button>
        </div>
      </div>
    </div>
  )
}
