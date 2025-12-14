# Usage Guide - Programmable PDF Editor

## Step 1: Access Your Deployed Application

### Get Your Frontend URL

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Select your project: `programmable-pdf-editor`
3. Click on the **Frontend** service
4. Go to **Settings** → **Networking**
5. You should see your public domain (e.g., `https://frontend-production-xxxx.up.railway.app`)
6. Click on the URL or copy it

### Verify Backend is Running

1. In the same Railway project, click on the **Backend** service
2. Go to **Settings** → **Networking**
3. Copy the backend URL (e.g., `https://backend-production-xxxx.up.railway.app`)
4. Test it in your browser - you should see: `{"message": "Programmable PDF Editor API"}`

### Update Environment Variables (If Needed)

**Frontend Service:**
- Go to **Variables** tab
- Ensure `NEXT_PUBLIC_API_URL` is set to your backend URL
- Example: `https://backend-production-xxxx.up.railway.app`

**Backend Service:**
- Go to **Variables** tab
- Ensure `CORS_ORIGINS` includes your frontend URL
- Example: `https://frontend-production-xxxx.up.railway.app,http://localhost:3000`

## Step 2: Using the Application

### 1. Open the Application

1. Navigate to your frontend URL in a web browser
2. You should see the "Programmable PDF Editor" interface

### 2. Upload a PDF

1. **Step 1: Upload PDF**
   - Click on the upload area or "Select PDF File" button
   - Choose a PDF file from your computer
   - Wait for the upload to complete (you'll see "✓ Uploaded: filename.pdf")
   - OCR processing will start automatically

### 3. Select Text Sections

1. **Step 2: Select Text Sections to Edit**
   - After OCR processing, you'll see detected text sections
   - Each section shows:
     - The detected text
     - Page number
     - Position coordinates
   - Click on sections you want to edit (they'll turn blue when selected)
   - You can select multiple sections

### 4. Configure Replacement Rules

1. **Step 3: Configure Replacement Rules**
   - For each selected section, configure:
   
   **Replacement Type:**
   - **Serial Number**: Sequential numbers (1, 2, 3, ...)
     - Set Start Value (e.g., 1)
   - **Random Number**: Random numbers within a range
     - Set Min Value (e.g., 100)
     - Set Max Value (e.g., 999)
   - **Custom**: For custom logic (currently same as serial)
   
   **Formatting Options:**
   - **Number Format**: e.g., `%04d` for zero-padded (0001, 0002, ...)
   - **Prefix**: Text before the number (e.g., "INV-")
   - **Suffix**: Text after the number (e.g., "-2024")
   
   **Preview**: See how your formatted text will look

### 5. Generate PDF Copies

1. **Step 4: Generate PDF Copies**
   - Enter the number of copies you want to generate (e.g., 10)
   - Click "Generate [X] PDF Copies"
   - Wait for processing (you'll see a progress bar)
   - A ZIP file will automatically download containing all generated PDFs

## Example Use Case: Invoice Numbers

### Scenario
You have an invoice PDF with invoice number "INV-001" and want to create 10 copies with sequential numbers.

### Steps:
1. **Upload** the invoice PDF
2. **Select** the text section containing "INV-001"
3. **Configure**:
   - Type: Serial Number
   - Start Value: 1
   - Prefix: "INV-"
   - Format: "%03d" (for 001, 002, 003...)
   - Suffix: "" (empty)
4. **Generate** 10 copies
5. **Download** the ZIP file with 10 invoices (INV-001, INV-002, ..., INV-010)

## Troubleshooting

### Can't Access the Frontend

1. **Check Railway Status**
   - Go to Railway dashboard
   - Verify the frontend service is running (green status)
   - Check the logs for any errors

2. **Verify Environment Variables**
   - Frontend: `NEXT_PUBLIC_API_URL` should point to your backend
   - Backend: `CORS_ORIGINS` should include your frontend URL

3. **Check Domain**
   - Make sure you're using the correct Railway-generated domain
   - Try refreshing the page

### PDF Upload Fails

1. **Check Backend Logs**
   - Go to Railway → Backend service → Logs
   - Look for error messages

2. **Verify File Size**
   - Large PDFs may take longer to process
   - Check Railway logs for timeout errors

3. **Check CORS Settings**
   - Ensure backend `CORS_ORIGINS` includes your frontend URL
   - Include the protocol (https://)

### OCR Not Working

1. **Check Backend Logs**
   - Look for Tesseract OCR errors
   - Verify Tesseract is installed (should be automatic with Nixpacks)

2. **PDF Quality**
   - Ensure PDF has readable text (not just images)
   - Scanned PDFs may need better quality

3. **Processing Time**
   - OCR can take time for large PDFs
   - Wait for processing to complete

### Generated PDFs Are Empty or Wrong

1. **Check Text Selection**
   - Ensure you selected the correct text section
   - Verify the original text matches what you see

2. **Check Replacement Rules**
   - Verify prefix/suffix are correct
   - Check number format is valid

3. **Check Backend Logs**
   - Look for PDF processing errors
   - Verify PyMuPDF is working correctly

## Local Development

If you want to test locally before deploying:

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Then access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Tips

1. **Start Small**: Test with a simple PDF first
2. **Check Preview**: Always check the preview in Step 3 before generating
3. **Multiple Sections**: You can edit multiple text sections at once
4. **Format Testing**: Test different formats (prefixes, suffixes) to get the desired output
5. **Monitor Logs**: Keep Railway logs open to see what's happening

## Support

- Check Railway logs for detailed error messages
- Review the README.md for setup instructions
- Check RAILWAY_DEPLOY.md for deployment issues

