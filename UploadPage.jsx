import React, { useState, useEffect, useRef } from "react";
import { Upload, PlayCircle, Loader, CheckCircle, Download } from "lucide-react";
import axios from "axios";
import "./Upload.css";

function UploadPage() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [fileType, setFileType] = useState("");
  const [processedFile, setProcessedFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const fileInputRef = useRef(null); // Reference for file input

  // Handle file selection
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(URL.createObjectURL(file));
      setFileType(file.type.startsWith("video") ? "video" : "image");
      setFileName(file.name);
    }
  };

  // Handle Upload Button Click (Resets States)
  const handleUploadClick = () => {
    setIsProcessing(false);
    setIsCompleted(false);
    setUploadedFile(null);
    setProcessedFile(null);
    setFileName("");

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Check processing status
  const checkProcessingStatus = async () => {
    try {
      const response = await axios.get("http://localhost:8000/status/");
      console.log("Status Response:", response.data);

      if (response.data.status === "completed") {
        setIsProcessing(false);
        setIsCompleted(true);
        fetchProcessedFile();
      }
    } catch (error) {
      console.log("Waiting for the processed file...");
    }
  };

  // Fetch processed video once ready
  const fetchProcessedFile = async () => {
    try {
      const response = await axios.get("http://localhost:8000/output/", {
        responseType: "blob",
      });

      if (response.status === 200) {
        const blob = new Blob([response.data], { type: "video/mp4" });
        const url = URL.createObjectURL(blob);
        setProcessedFile(url);
        console.log("Processed file is ready:", url);
      }
    } catch (error) {
      console.error("Error fetching processed file:", error);
    }
  };

  // Poll for processing status every 3 seconds when processing
  useEffect(() => {
    let interval;
    if (isProcessing) {
      interval = setInterval(checkProcessingStatus, 3000);
    }
    return () => clearInterval(interval);
  }, [isProcessing]);

  // Handle file upload and processing
  const handleProcess = async () => {
    if (!uploadedFile) return alert("Please upload a file first!");

    setIsProcessing(true);
    setIsCompleted(false);
    setProcessedFile(null);

    const formData = new FormData();
    formData.append("file", document.getElementById("fileInput").files[0]);

    try {
      const response = await axios.post("http://localhost:8000/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (response.data.status === "completed") {
        console.log("✅ File uploaded and processed successfully.");
        checkProcessingStatus();
      } else {
        console.error("❌ Error in processing:", response.data);
        alert("Error in processing the file. Please try again.");
      }
    } catch (error) {
      console.error("Error processing file:", error);
      alert("Failed to process the file. Please try again.");
      setIsProcessing(false);
    }
  };

  // Handle file download
  const handleDownload = async () => {
    if (!processedFile) return alert("No processed file available!");
  
    try {
      const response = await axios.get("http://localhost:8000/download/", {
        responseType: "blob",
      });
  
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `processed_${fileName || "file"}.mp4`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error downloading file:", error);
    }
  };
  

  return (
    <div className="page-container">
      <header className="header">
        <h1 className="header-title">Vehicle Monitoring System</h1>
        <button className="header-upload-button" onClick={handleUploadClick}>
          Upload
        </button>
      </header>

      <div className="upload-card">
        {!isProcessing && !isCompleted && (
          <>
            <h2 className="card-title">Upload a Video or Image</h2>
            <div className="drag-drop-zone">
              <Upload className="upload-icon" />
              <p>Drag & Drop files here</p>

              <input
                type="file"
                id="fileInput"
                className="file-input"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept="image/*, video/*"
              />
              <label htmlFor="fileInput" className="choose-file-button">
                Choose File
              </label>

              {uploadedFile && <p className="success-message">File uploaded successfully!</p>}
            </div>

            <button className="process-file-button" onClick={handleProcess}>
              <PlayCircle className="icon" /> Process File
            </button>
          </>
        )}

        {isProcessing && (
          <>
            <h2 className="card-title">Processing...</h2>
            <Loader className="processing-icon spin-animation" />
            <p className="processing-text">Please wait while we process your file.</p>
          </>
        )}

        {isCompleted && (
          <>
            <h2 className="card-title">Processing Complete!</h2>
            <CheckCircle className="completed-icon" />
            <p className="processing-text">Your processed file is ready for review.</p>

            {processedFile && (
              <>
                <button
      className="download-button"
      onClick={() => {
        const link = document.createElement("a");
        link.href = processedFile;
        link.setAttribute("download", `processed_${fileName || "file"}.mp4`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }}
    >
      <Download className="icon" /> Download File
    </button>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default UploadPage;
