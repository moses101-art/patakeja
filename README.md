# PataKeja: setup guide (no coding needed)

You will do 6 short steps, all in the browser. Total cost to start: KSh 0 (domain is optional, about KSh 1,000 to 1,500 a year).

## What is in this folder
- `index.html`: the public website (tenants browse, landlords post)
- `admin.html`: your private page to approve listings and handle reports
- `config.js`: where you paste your two Supabase values
- `supabase.sql`: sets up the database and photo storage

## Step 1: Create a free Supabase account
1. Go to **supabase.com** and sign up (Google login is fine).
2. Click **New project**. Name it `patakeja`. Choose a strong database password and save it somewhere safe.
3. For region, pick the one closest to Kenya (for example Europe or South Africa if offered).
4. Wait about 2 minutes until the project is ready.

## Step 2: Create the database
1. In Supabase, open **SQL Editor** (left menu) and click **New query**.
2. Open `supabase.sql` in Notepad, copy everything, paste it into the editor.
3. Click **Run**. You should see "Success".

## Step 3: Create your admin login
1. Go to **Authentication > Users > Add user > Create new user**.
2. Enter your email and a strong password. Tick "Auto confirm user".
3. IMPORTANT: go to **Authentication > Sign In / Providers** (or Settings) and **turn OFF "Allow new users to sign up"**. Otherwise strangers could create admin accounts.

## Step 4: Copy your two keys
1. Open **Project Settings > API**.
2. Copy the **Project URL** and the **anon public key**.

## Step 5: Paste them into config.js
1. Open `config.js` in Notepad.
2. Replace the two placeholder texts with the URL and key. Keep the quotation marks.
3. Put your WhatsApp number in the same file. Save.

## Step 6: Put the site online (free)
Easiest option: **Netlify Drop**
1. Go to **app.netlify.com/drop** and sign up.
2. Drag the whole `patakeja-site` folder onto the page.
3. You get a link like `something.netlify.app`. Your site is live.
4. Later, buy `patakeja.co.ke` and connect it in Netlify under **Domain settings**.

Admin page: `your-link/admin.html`. Log in with the email and password from Step 3. Do not share this link.

## Test it before you tell anyone
1. Open your site and click **List a vacant house**. Post a test house with 3 photos.
2. Open `/admin.html`, log in, and **Approve** it.
3. Refresh the public site. The house should appear, and the map pin should show.
4. Tap the house, **Show contact**, and check the phone and directions.
5. Use the owner code to mark it taken, then confirm it disappears.
6. Test on a cheap Android phone with mobile data.

## How it works day to day
- Landlords and caretakers post themselves (free). Nothing goes public until you approve it.
- You can also post for a landlord using the same form, then approve it.
- Listings expire automatically after 30 days. Use **Renew** in admin if the house is still vacant.
- After posting, the owner gets a 6-letter code to mark the house as taken. Tell caretakers to screenshot it.
- Tenants can **Report** a listing. You see it in the Reports tab.

## Not included yet (next phases)
- **M-Pesa KSh 100 unlock.** The database already hands out contacts one listing at a time (`get_contact`), so the paywall plugs in there. Needs a developer for Daraja STK Push.
- SMS or WhatsApp reminders at day 25 (needs an SMS provider such as Africa's Talking).
- Login for landlords with phone OTP, stats per landlord, pin clustering on the map.
- Daily database backups: on the free Supabase plan, export data manually from time to time.

## Limits to know
- Free Supabase pauses a project after a week of no activity and has storage limits. Photos are compressed to about 200 KB, so 1 GB holds thousands.
- Anyone can submit a listing. Because you approve each one, spam stays hidden, but check phone numbers before approving.
- Phone numbers are only returned one listing at a time, but a determined person can still collect them. That is normal for listing sites.

## If something goes wrong
- "Setup not finished" banner: config.js still has placeholders.
- Photos fail to upload: re-run `supabase.sql` or check **Storage** has a public bucket named `photos`.
- Cannot log in to admin: confirm the user exists in Authentication and sign ups are off but the user was created.
Send me the exact error text and I will fix it.
