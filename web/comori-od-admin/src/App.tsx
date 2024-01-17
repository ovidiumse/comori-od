import React, { useEffect, useRef, useState } from 'react';
import logo from './logo.svg';
import './App.css';
import { Button, Card, Form, Stack } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import { upload } from '@testing-library/user-event/dist/upload';

function App() {
  const [otp, setOTP] = useState("")
  const [lines, setLines] = useState([] as any)
  const [hasMore, setHasMore] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const bottom = useRef<HTMLDivElement>(null)

  function onOTPChange(args: any) {
    if (args && args?.target) {
      setOTP(args.target.value)
    }
  }

  function checkStatus() {
    console.log(`Checking uploading status`)
    fetch("http://localhost:8091/upload")
    .then(async response => {
      if (response.status !== 200) {
        const data = await response.json()

        throw `Checking uploading task failed! Error: '${data["message"]}'`
      }

      return response.json()
    })
    .then(response => {
      let output = []
      for (const line of response["output"]) {
        output.push({color: 'black', message: line})
      }

      for (const line of response["errors"]) {
        output.push({color: 'red', message: line})
      }

      setLines([
        ...lines,
        ...output
      ])
      
      setHasMore(hasMore + 1)
    })
    .catch(error => {
      console.log(`Error: ${error}`)
      setHasMore(0)
      setIsLoading(false)
    })
  }

  useEffect(() => {
    if (hasMore) {
      checkStatus()
    }

    bottom.current?.scrollIntoView({
      block: "end"
    })
  }, [hasMore, lines.length])

  function upload() {
    console.log(`Starting upload...`)
    setLines([])
    setIsLoading(true)

    fetch("http://localhost:8091/upload", { 
        method: 'POST', 
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ API_TOTP_KEY: otp})
      })
      .then(async response => {
        if (response.status !== 200) {
          const data = await response.json()
          throw `Checking uploading task failed! Error: '${data["message"]}'`
        }

        return response.json()
      })
      .then(response => {
          checkStatus()
      })
      .catch(error => {
        console.log(`Error: ${error}`)
      })
  }
  
  return (
    <div className="App">
      <Stack style={{justifyContent: "center", height: "100%"}}>
        <Stack direction='horizontal' style={{alignSelf: "center"}}>
          <Card>
            <Card.Body>
              <Stack gap={3}>
                <Card.Title>
                  <b>Administrare conținut Comori OD (testapi)</b>
                </Card.Title>
                <Form onSubmit={(event) => {
                    event.preventDefault()
                    if (otp.length === 6) {
                      upload()
                    }
                }}>
                  <Form.Group controlId='uploadForm.OTPInput'>
                    <Form.Control name="otp" type='number' onChange={onOTPChange} placeholder="Introduceți parola"/>
                  </Form.Group>
                </Form>
                <Stack id="logs" style={{textAlign: "left", width: "1200px", height: "500px", overflowY: "auto", border: "1px solid lightgray"}}>
                    <ul style={{listStyle: "none"}}>
                      {
                        lines.map((line: any, index: number) => {
                          return (
                            <li key={index + line}><code style={{color: line.color}}>{line.message}</code></li>
                          )
                        })
                      }
                    </ul>
                    <div ref={bottom}/>
                </Stack>
                <Stack direction='horizontal' style={{width: "100%", justifyContent: "flex-end"}}>
                  <Button variant="primary" disabled={otp.length < 6 || isLoading} onClick={() => {upload()}}>{isLoading ? 'Se încarcă...' : 'Încarcă'}</Button>
                </Stack>
              </Stack>
            </Card.Body>
          </Card>
        </Stack>
      </Stack>
    </div>
  );
}

export default App;
