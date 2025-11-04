# 3D Printing Web Service - Project Vision

## 🎯 High-Level Goal

Build a **web-based 3D printing service** that allows users to upload STL files through a frontend, which then automatically slices and sends them to your Bambu Lab P1P printer for printing.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Frontend Web Service)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ Upload STL
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      SUPABASE STORAGE                           │
│                   (Cloud File Storage)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │ Trigger Event
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICE                              │
│              (This OrcaSlicer CLI Project)                      │
│                                                                 │
│  1. Detect new STL file in Supabase                            │
│  2. Download STL to local staging                              │
│  3. Run OrcaSlicer CLI to slice                                │
│  4. Generate G-code                                            │
│  5. Upload G-code to printer via FTP                           │
│  6. (Optional) Update job status in database                   │
└────────────────────────────┬────────────────────────────────────┘
                             │ FTP Upload
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BAMBU LAB P1P PRINTER                        │
│                     (192.168.1.129)                             │
│                                                                 │
│  - Receives G-code via FTPS                                    │
│  - Starts printing automatically                               │
│  - Reports status back (optional)                              │
└─────────────────────────────────────────────────────────────────┘
```

## 🧩 Components Breakdown

### 1. Frontend Web Service (To Build)
**Purpose:** User interface for uploading 3D models

**Tech Stack Options:**
- React/Next.js + Supabase JS Client
- Vue.js + Supabase
- Simple HTML/JS with Supabase

**Features:**
- File upload (STL files)
- Print queue visualization
- Job status tracking
- User authentication (optional)
- Print history

**Key Functions:**
```javascript
// Upload STL to Supabase Storage
async function uploadSTL(file) {
  const { data, error } = await supabase.storage
    .from('stl-files')
    .upload(`uploads/${file.name}`, file)
  
  // Trigger backend processing
  await supabase.from('print_jobs').insert({
    filename: file.name,
    status: 'pending',
    storage_path: data.path
  })
}
```

### 2. Supabase (Cloud Infrastructure)
**Purpose:** File storage and job queue management

**Components:**
- **Storage Bucket:** `stl-files` - Stores uploaded STL files
- **Database Table:** `print_jobs` - Tracks print job status
- **Edge Functions/Webhooks:** Trigger backend when new file uploaded

**Database Schema:**
```sql
CREATE TABLE print_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  filename TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  status TEXT DEFAULT 'pending', -- pending, slicing, uploading, printing, complete, failed
  uploaded_at TIMESTAMP DEFAULT NOW(),
  sliced_at TIMESTAMP,
  gcode_path TEXT,
  error_message TEXT,
  printer_ip TEXT DEFAULT '192.168.1.129'
);
```

### 3. Backend Service (Current Project - OrcaSlicer CLI)
**Purpose:** Automated slicing and printer communication

**Current Status:**
- ✅ OrcaSlicer CLI built from source
- ✅ Validation bug fixed
- ✅ FTP upload to P1P working
- ⚠️ Runtime segfault needs debugging

**What It Does:**
1. **Monitor** Supabase for new STL files
2. **Download** STL from Supabase Storage
3. **Slice** using OrcaSlicer CLI with P1P profiles
4. **Generate** G-code output
5. **Upload** G-code to printer via FTPS
6. **Update** job status in database

**Key Script:** `~/AI_PIPELINE/slice_pipeline.sh`

**Integration Points:**
```bash
# This script needs to be triggered by Supabase
# Options:
# 1. Supabase Edge Function calls this via webhook
# 2. Polling service checks database every N seconds
# 3. Supabase Realtime subscription triggers processing
```

### 4. Bambu Lab P1P Printer
**Purpose:** Physical 3D printer that receives and executes G-code

**Connection Details:**
- **IP:** 192.168.1.129
- **Protocol:** FTPS (port 990)
- **Credentials:** user: `bblp`, password: `30551719`

**Current Status:** ✅ FTP upload working

## 🔄 Complete Workflow

### User Journey:
1. User visits web frontend
2. User uploads STL file
3. File stored in Supabase Storage
4. Database record created with status "pending"
5. Backend service detects new job
6. Backend downloads STL
7. Backend slices STL → G-code
8. Backend uploads G-code to printer
9. Printer starts printing
10. User sees status update: "printing"

### Data Flow:
```
STL File (User) 
  → Supabase Storage 
  → Backend Service (~/AI_PIPELINE/LOCKED_SPLIT_STAGE/)
  → OrcaSlicer CLI
  → G-code (~/AI_PIPELINE/SLICED_OUTPUT/)
  → Printer (192.168.1.129)
  → Physical Print
```

## 🛠️ What We've Built So Far

### ✅ Completed:
1. **OrcaSlicer CLI Integration**
   - Custom build from source
   - Validation bug identified and fixed
   - Profile system understood

2. **Printer Communication**
   - FTP upload working
   - Printer discovered on network
   - Access credentials configured

3. **Automation Scripts**
   - `slice_pipeline.sh` - Main automation
   - Profile management
   - Error handling

4. **Documentation**
   - Complete architecture docs
   - Build process documented
   - Troubleshooting guides

### ⚠️ Current Blocker:
- Custom OrcaSlicer binary segfaults in CLI mode
- **Workaround:** Use GUI or debug the crash

### 🚧 Still To Build:
1. **Frontend Web Service**
   - User interface
   - File upload
   - Job status display

2. **Supabase Integration**
   - Storage bucket setup
   - Database tables
   - Trigger mechanism

3. **Backend Service Wrapper**
   - Supabase file monitoring
   - Job queue processing
   - Status updates

4. **Deployment**
   - Host backend service (VPS, cloud, local server)
   - Configure webhooks/triggers
   - Set up monitoring

## 📋 Implementation Roadmap

### Phase 1: Fix Current Issues (Now)
- [ ] Debug OrcaSlicer CLI segfault
- [ ] Test end-to-end slicing locally
- [ ] Verify FTP upload reliability

### Phase 2: Supabase Setup (Next)
- [ ] Create Supabase project
- [ ] Set up storage bucket for STL files
- [ ] Create `print_jobs` database table
- [ ] Configure storage webhooks/triggers

### Phase 3: Backend Integration
- [ ] Create Supabase listener service
- [ ] Integrate with `slice_pipeline.sh`
- [ ] Add database status updates
- [ ] Implement error handling & logging

### Phase 4: Frontend Development
- [ ] Build upload interface
- [ ] Add job queue display
- [ ] Implement status polling
- [ ] Add user authentication (optional)

### Phase 5: Deployment & Testing
- [ ] Deploy backend service
- [ ] Deploy frontend
- [ ] End-to-end testing
- [ ] Production monitoring

## 💻 Technology Stack

### Current (Backend):
- **Language:** Bash scripting
- **Slicer:** OrcaSlicer CLI (custom build)
- **File Transfer:** curl with FTPS
- **OS:** macOS (can port to Linux)

### Planned (Full Stack):
- **Frontend:** React/Next.js or Vue.js
- **Backend:** Node.js or Python wrapper around bash scripts
- **Database:** Supabase (PostgreSQL)
- **Storage:** Supabase Storage (S3-compatible)
- **Hosting:** Vercel/Netlify (frontend), VPS/Cloud (backend)
- **Queue:** Supabase Realtime or polling

## 🎯 Key Integration Points

### 1. Supabase → Backend Trigger
**Options:**
```javascript
// Option A: Supabase Edge Function
export async function handleUpload(req) {
  const { filename, path } = await req.json()
  
  // Call your backend service
  await fetch('https://your-backend.com/slice', {
    method: 'POST',
    body: JSON.stringify({ filename, path })
  })
}

// Option B: Realtime Subscription (in backend)
supabase
  .from('print_jobs')
  .on('INSERT', payload => {
    // Trigger slice_pipeline.sh
    processJob(payload.new)
  })
  .subscribe()

// Option C: Polling (simple but less efficient)
setInterval(async () => {
  const { data } = await supabase
    .from('print_jobs')
    .select('*')
    .eq('status', 'pending')
  
  data.forEach(job => processJob(job))
}, 5000) // Check every 5 seconds
```

### 2. Backend → Supabase Updates
```bash
# In slice_pipeline.sh, add status updates
update_status() {
  local job_id=$1
  local status=$2
  
  curl -X PATCH "https://your-project.supabase.co/rest/v1/print_jobs?id=eq.$job_id" \
    -H "apikey: YOUR_SUPABASE_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"status\": \"$status\"}"
}
```

## 🔐 Security Considerations

1. **File Validation:** Check STL files for malicious content
2. **Authentication:** Require user login for uploads
3. **Rate Limiting:** Prevent abuse
4. **Access Control:** Secure printer credentials
5. **Network Security:** Printer on isolated VLAN (optional)

## 📊 Future Enhancements

- **Multi-printer support:** Queue jobs across multiple printers
- **Material selection:** Let users choose filament type
- **Print estimation:** Show time/cost before printing
- **Live monitoring:** Webcam feed from printer
- **Email notifications:** Alert when print completes
- **Print history:** Gallery of completed prints
- **Slicing options:** Custom quality/speed settings

## 🎉 Summary

**You're building:** A web service that lets users upload STL files and automatically prints them on your P1P printer.

**Current state:** Backend slicing & printer communication is 95% done. Just need to fix the CLI crash, then build the web frontend and Supabase integration.

**Next immediate step:** Debug the OrcaSlicer segfault, then move to Supabase setup.

---

**This is a really cool project!** You're essentially building a "print-on-demand" service for 3D printing. Once complete, anyone with access can upload a model and have it automatically printed. 🚀
