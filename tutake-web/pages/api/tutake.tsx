import axios from "axios";

const get_jobs = async (event: any) => {
    event.preventDefault()

    await axios.get(`http://127.0.0.1:5000/api/jobs`)
        .then((resp) => {
            return resp.data
        })
}