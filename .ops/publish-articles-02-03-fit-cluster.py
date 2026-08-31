import base64,hashlib,html,json,os,re,ssl,time,urllib.error,urllib.parse,urllib.request
host=os.environ['CPANEL_HOST'];user=os.environ['CPANEL_USER'];token=os.environ['CPANEL_TOKEN'];root=os.environ['THEME_ROOT'].strip('/');healthy=os.environ.get('HEALTHY_HOME_SHA','');ctx=ssl._create_unverified_context()
A1_SLUG='تیشرت-باکسی-چیست-تفاوت-اورسایز'
A2={
 'key':'a02','marker':'wave1-a02',
 'title':'راهنمای انتخاب سایز تیشرت باکسی مردانه',
 'slug':'راهنمای-انتخاب-سایز-تیشرت-باکسی-مردانه',
 'seo_title':'راهنمای انتخاب سایز تیشرت باکسی مردانه | اندازه‌گیری دقیق',
 'seo_desc':'برای انتخاب سایز تیشرت باکسی مردانه، عرض سینه، قد، سرشانه و آستین را درست اندازه بگیرید و بین دو سایز بر اساس فیت دلخواه تصمیم بگیرید.',
 'excerpt':'برای انتخاب سایز تیشرت باکسی فقط به M یا L تکیه نکنید. با چند اندازه‌گیری ساده می‌توانید فیت واقعی لباس را قبل از خرید بهتر پیش‌بینی کنید.',
 'focus':'سایز تیشرت باکسی مردانه',
 'body':'''<p>برای انتخاب سایز تیشرت باکسی مردانه، مهم‌ترین اصل این است که <strong>سایز اسمی را با اندازه واقعی لباس اشتباه نگیریم</strong>. یک تیشرت M در دو برند مختلف می‌تواند عرض سینه، قد، سرشانه و آستین متفاوتی داشته باشد. به همین دلیل بهترین روش این است که چند اندازه اصلی محصول را با تیشرتی که همین حالا تن‌خورش را دوست دارید مقایسه کنید.</p>
<p>اگر هنوز درباره فرم این مدل مطمئن نیستید، ابتدا راهنمای <a href="__A1_URL__">تفاوت تیشرت باکسی و اورسایز</a> را بخوانید. بعد از آن، انتخاب سایز بسیار ساده‌تر می‌شود چون می‌دانید قرار است چه نسبتی بین عرض و قد لباس حفظ شود.</p>

<h2>چرا سایز اسمی برای تیشرت باکسی کافی نیست؟</h2>
<p>در فیت باکسی، شخصیت لباس از نسبت‌ها می‌آید. معمولاً تنه آزادتر است، قد کنترل‌شده‌تر می‌ماند و سرشانه یا آستین می‌تواند افت بیشتری نسبت به یک تیشرت استاندارد داشته باشد. بنابراین انتخاب یک سایز بزرگ‌تر از روی عادت ممکن است به‌جای «باکسی‌تر شدن»، فقط قد لباس را زیاد کند و فرم اصلی را به سمت اورسایز ببرد.</p>
<p>برای همین، هنگام خرید آنلاین بهتر است به‌جای پرسیدن «من همیشه L می‌پوشم، همین را بگیرم؟» این سؤال را بپرسید: <strong>اندازه‌های L این مدل نسبت به تیشرت مرجع من چقدر فرق دارد؟</strong></p>

<h2>چه اندازه‌هایی را باید بررسی کنیم؟</h2>
<h3>۱. عرض سینه</h3>
<p>تیشرت را روی سطح صاف بگذارید و فاصله زیر بغل تا زیر بغل را به‌صورت خط مستقیم اندازه بگیرید. این عدد یکی از مهم‌ترین نشانه‌های آزادی تنه است. اگر محصول باکسی است، معمولاً انتظار داریم این عرض از یک فیت استاندارد بیشتر باشد.</p>

<h3>۲. قد لباس</h3>
<p>از بالاترین نقطه سرشانه کنار یقه تا لبه پایین تیشرت را اندازه بگیرید. در تیشرت باکسی، قد نقش بسیار مهمی دارد؛ چون اگر بیش از حد بلند شود، فرم چهارگوش و جمع‌وجور لباس ضعیف‌تر می‌شود.</p>

<h3>۳. عرض سرشانه</h3>
<p>فاصله دو نقطه دوخت سرشانه را اندازه بگیرید. اگر مدل سرشانه افتاده دارد، عدد بزرگ‌تر طبیعی است. اما میزان افتی که زیبا به نظر می‌رسد کاملاً به سلیقه و استایل موردنظر شما بستگی دارد.</p>

<h3>۴. طول و پهنای آستین</h3>
<p>آستین در یک باکسی مردانه معمولاً از فیت کلاسیک آزادتر است. اگر دوست دارید آستین نزدیک میانه بازو یا حوالی آرنج قرار بگیرد، طول آستین و عرض دهانه آن را هم با لباس مرجع مقایسه کنید.</p>

<h2>چطور تیشرت مرجع خودمان را اندازه بگیریم؟</h2>
<ol>
<li>تیشرتی را انتخاب کنید که تن‌خورش روی بدنتان نزدیک به چیزی است که می‌خواهید.</li>
<li>آن را بدون کشیدن پارچه روی سطح صاف قرار دهید.</li>
<li>عرض سینه، قد، سرشانه و آستین را ثبت کنید.</li>
<li>اعداد را با جدول اندازه همان محصول مقایسه کنید، نه با جدول یک محصول یا برند دیگر.</li>
</ol>
<p>این روش از اندازه‌گیری مستقیم دور بدن برای بسیاری از خریدهای آنلاین ساده‌تر است، چون دارید «لباسی با فیت مطلوب» را با «لباس جدید» مقایسه می‌کنید.</p>

<h2>اگر بین دو سایز هستیم چه کنیم؟</h2>
<p>اول مشخص کنید چه نتیجه‌ای می‌خواهید. اگر می‌خواهید فرم باکسی جمع‌وجورتر و قد کنترل‌شده‌تر بماند، معمولاً سایزی که به اندازه مرجع شما نزدیک‌تر است انتخاب منطقی‌تری خواهد بود. اگر حجم بیشتر، افت سرشانه واضح‌تر و ظاهر رها‌تری می‌خواهید، سایز بزرگ‌تر می‌تواند مناسب‌تر باشد؛ البته به شرطی که افزایش قد هم برایتان قابل قبول باشد.</p>
<p>به‌جای قانون ثابت «یک سایز بالا» یا «یک سایز پایین»، اختلاف واقعی اعداد را ببینید. ممکن است بین دو سایز فقط دو سانتی‌متر اختلاف عرض وجود داشته باشد اما قد تقریباً ثابت بماند؛ یا برعکس، تغییر قد محسوس‌تر باشد.</p>

<h2>قد و فرم بدن چقدر در انتخاب سایز مهم است؟</h2>
<p>قد و نسبت‌های بدن روی نحوه دیده‌شدن لباس اثر دارند، اما قرار نیست یک سایز را به‌صورت قطعی برای یک فرم بدن تجویز کنیم. دو نفر با قد مشابه می‌توانند به‌دلیل طول تنه، عرض شانه یا استایل موردنظر، انتخاب متفاوتی داشته باشند.</p>
<p>نکته کاربردی این است که ببینید لبه پایین تیشرت نسبت به کمر و فاق شلوارتان کجا قرار می‌گیرد. اگر شلوار فاق‌بلند یا حجم‌دار می‌پوشید، قد کنترل‌شده تیشرت می‌تواند بخش بیشتری از فرم شلوار را نشان دهد. برای مقایسه حجم پایین‌تنه نیز راهنمای <a href="__A3_URL__">تفاوت شلوار بگ، نیم‌بگ و فول‌بگ</a> کمک می‌کند.</p>

<h2>فیت باکسی را با چه شلواری بسنجیم؟</h2>
<p>بهتر است تیشرت را جدا از کل استایل تصمیم‌گیری نکنید. یک باکسی نسبتاً کوتاه با شلوار آزاد می‌تواند تعادل خوبی بسازد، در حالی که همان تیشرت با شلوار بسیار جذب ظاهر متفاوتی خواهد داشت. اگر قصد دارید بیشتر با بگ و نیم‌بگ ست کنید، علاوه بر عرض تیشرت به قد آن هم توجه ویژه داشته باشید تا هر دو بخش استایل بی‌دلیل روی هم نیفتند.</p>

<h2>اشتباه‌های رایج در انتخاب سایز تیشرت باکسی</h2>
<h3>فقط به قد و وزن نگاه می‌کنیم</h3>
<p>قد و وزن می‌توانند سرنخ اولیه باشند، اما برای پیش‌بینی فیت دقیق کافی نیستند. نسبت شانه، طول تنه و حتی ترجیح شخصی شما در میزان آزادی لباس مهم است.</p>

<h3>باکسی را با تیشرت معمولی سایز بزرگ یکی می‌دانیم</h3>
<p>الگوی باکسی از ابتدا با نسبت‌های مشخص طراحی می‌شود. اگر فقط یک تیشرت استاندارد را بزرگ‌تر بخرید، ممکن است قد و یقه و حلقه آستین به شکل مطلوب شما تغییر نکنند.</p>

<h3>جدول اندازه را بدون لباس مرجع می‌خوانیم</h3>
<p>دیدن عدد ۶۰ سانتی‌متر برای عرض سینه به‌تنهایی معنای زیادی ندارد. وقتی بدانید تیشرت محبوب شما مثلاً چند سانتی‌متر عرض دارد، همان عدد تبدیل به معیار قابل استفاده می‌شود.</p>

<h2>سؤال‌های رایج درباره سایز تیشرت باکسی</h2>
<h3>آیا برای تیشرت باکسی باید یک سایز کوچک‌تر بگیریم؟</h3>
<p>نه به‌صورت عمومی. اگر مدل از ابتدا باکسی طراحی شده باشد، ابتدا جدول اندازه همان مدل را با لباس مرجع مقایسه کنید. کوچک‌تر گرفتن می‌تواند آزادی موردنظر طراح را از بین ببرد.</p>

<h3>مهم‌ترین عدد برای انتخاب سایز کدام است؟</h3>
<p>یک عدد کافی نیست. برای باکسی، نسبت <strong>عرض سینه به قد</strong> اهمیت زیادی دارد و بعد از آن سرشانه و آستین تصویر کامل‌تری از تن‌خور می‌دهند.</p>

<h3>اگر عرض مناسب باشد ولی قد بلند باشد چه کنیم؟</h3>
<p>در این حالت سایز کوچک‌تر را با دقت بررسی کنید، اما فقط در صورتی که کاهش عرض و سرشانه هم همچنان با فیت دلخواهتان هماهنگ باشد. گاهی مسئله از الگوی همان مدل است و نه از سایز.</p>

<h2>جمع‌بندی</h2>
<p>برای انتخاب سایز تیشرت باکسی مردانه، از سایز اسمی شروع نکنید؛ از یک تیشرت مرجع شروع کنید. عرض سینه، قد، سرشانه و آستین را مقایسه کنید و بعد بر اساس میزان آزادی و فرم کلی که می‌خواهید بین سایزها تصمیم بگیرید. این روش ساده، احتمال انتخاب اشتباه را بسیار کمتر می‌کند.</p>
<p><a href="/shop/">مشاهده محصولات Gramiss</a>؛ هنگام بررسی هر محصول، اندازه و توضیح فیت همان مدل را معیار اصلی انتخاب قرار دهید.</p>'''
}
A3={
 'key':'a03','marker':'wave1-a03',
 'title':'تفاوت شلوار بگ، نیم‌بگ و فول‌بگ؛ کدام فیت مناسب شماست؟',
 'slug':'تفاوت-شلوار-بگ-نیم-بگ-فول-بگ',
 'seo_title':'تفاوت شلوار بگ، نیم‌بگ و فول‌بگ | راهنمای انتخاب فیت',
 'seo_desc':'فرق شلوار بگ، نیم‌بگ و فول‌بگ را از نظر حجم ران، زانو، دمپا و فرم کلی بشناسید و بر اساس استایل و تن‌خور دلخواه فیت مناسب را انتخاب کنید.',
 'excerpt':'بگ، نیم‌بگ و فول‌بگ فقط سه اسم برای یک شلوار گشاد نیستند. تفاوت حجم ران، زانو و دمپا می‌تواند فرم نهایی استایل را کاملاً عوض کند.',
 'focus':'تفاوت شلوار بگ نیم بگ فول بگ',
 'body':'''<p>تفاوت شلوار بگ، نیم‌بگ و فول‌بگ بیشتر از یک اسم روی برچسب است. چیزی که واقعاً فیت را می‌سازد، <strong>حجم شلوار از ران تا زانو و دمپا، قد، فاق و نحوه ریزش پارچه</strong> است. به همین دلیل ممکن است دو فروشگاه از یک واژه استفاده کنند اما اندازه‌های واقعی محصولاتشان یکسان نباشد.</p>
<p>اگر بخواهیم خیلی خلاصه بگوییم: نیم‌بگ معمولاً آزاد اما کنترل‌شده‌تر است، بگ حجم واضح‌تری در کل پا می‌سازد و فول‌بگ بیشترین حجم و ریزش را در سیلوئت ایجاد می‌کند. با این حال برای خرید دقیق، همیشه اندازه واقعی همان محصول را بالاتر از اسم فیت قرار دهید.</p>

<h2>شلوار نیم‌بگ چیست؟</h2>
<p>نیم‌بگ یا <span dir="ltr">Semi-Baggy</span> معمولاً بین یک شلوار آزاد معمولی و بگ کامل قرار می‌گیرد. ران و زانو فضای کافی دارند، اما حجم شلوار آن‌قدر زیاد نیست که سیلوئت کاملاً حجیم شود. دمپا هم بسته به الگو می‌تواند نسبتاً باز باشد، ولی معمولاً کنترل‌شده‌تر از فول‌بگ دیده می‌شود.</p>
<ul>
<li>آزادی مناسب در ران و زانو</li>
<li>حجم بصری متوسط</li>
<li>ست‌کردن ساده‌تر با تیشرت‌های استاندارد، باکسی یا پیراهن آزاد</li>
<li>گزینه مناسب برای کسی که فیت آزاد می‌خواهد اما نمی‌خواهد شلوار مرکز اصلی حجم استایل باشد</li>
</ul>

<h2>شلوار بگ چیست؟</h2>
<p>در شلوار بگ یا <span dir="ltr">Baggy</span> آزادی از بالای پا تا پایین واضح‌تر است. ران فضای بیشتری دارد، زانو کمتر جمع می‌شود و دمپا معمولاً بازتر دیده می‌شود. قد شلوار هم اغلب طوری انتخاب می‌شود که با کفش ارتباط بصری داشته باشد و ممکن است کمی روی کتونی بنشیند.</p>
<p>بگ خوب قرار نیست صرفاً «چند سایز بزرگ‌تر» باشد. فاق، جای جیب، عرض کمر و مسیر درزها باید همچنان متناسب با الگوی لباس طراحی شده باشند.</p>

<h2>فول‌بگ چه فرقی با بگ دارد؟</h2>
<p>فول‌بگ یا <span dir="ltr">Full Baggy</span> حجم را یک مرحله جلوتر می‌برد. معمولاً فضای ران بیشتر، خط پا عریض‌تر و دمپای بازتری دارد و پارچه در حرکت، حضور بیشتری در استایل نشان می‌دهد. در بعضی مدل‌ها قد بلندتر هم به این حس کمک می‌کند.</p>
<p>نکته مهم این است که «فول‌بگ» استاندارد عددی جهانی ندارد. برای تشخیص واقعی، جدول اندازه و تصاویر تن‌خور همان محصول را ببینید.</p>

<h2>تفاوت نیم‌بگ، بگ و فول‌بگ را از روی چه اندازه‌هایی بفهمیم؟</h2>
<h3>۱. عرض ران</h3>
<p>هرچه عرض ران بیشتر باشد، حجم شلوار از بالاترین بخش پا زودتر خودش را نشان می‌دهد. این اندازه برای تشخیص بگ و فول‌بگ بسیار مهم است.</p>

<h3>۲. عرض زانو</h3>
<p>اگر شلوار از ران آزاد باشد اما در زانو به‌وضوح جمع شود، سیلوئت آن با یک بگ واقعی متفاوت خواهد شد. فاصله بین عرض ران و زانو نشان می‌دهد شلوار چقدر به سمت پایین باریک می‌شود.</p>

<h3>۳. عرض دمپا</h3>
<p>دمپا روی رابطه شلوار با کفش اثر مستقیم دارد. دمپای بازتر بخش بیشتری از کتونی را می‌پوشاند و ظاهر حجیم‌تری ایجاد می‌کند؛ دمپای کنترل‌شده‌تر فرم مرتب‌تری می‌دهد.</p>

<h3>۴. قد و فاق</h3>
<p>قد بلندتر می‌تواند باعث شکست یا چین روی کفش شود. فاق هم جای کمر و نسبت بالاتنه به پایین‌تنه را تغییر می‌دهد. بنابراین دو شلوار با عرض مشابه اما قد و فاق متفاوت ممکن است روی بدن کاملاً متفاوت دیده شوند.</p>

<h2>کدام فیت برای استایل شما مناسب‌تر است؟</h2>
<p>به‌جای پیدا کردن یک «فیت درست برای همه»، بهتر است میزان حجمی را انتخاب کنید که با استایل خودتان هماهنگ است.</p>
<ul>
<li><strong>نیم‌بگ:</strong> اگر آزادی می‌خواهید اما ظاهر نسبتاً کنترل‌شده و استفاده روزمره ساده‌تر برایتان مهم است.</li>
<li><strong>بگ:</strong> اگر می‌خواهید حجم شلوار بخشی واضح از استایل باشد و با کتونی و بالاتنه آزاد ترکیب شود.</li>
<li><strong>فول‌بگ:</strong> اگر عمداً دنبال سیلوئت حجیم، خیابانی‌تر و ریزش بیشتر پارچه هستید.</li>
</ul>
<p>هیچ‌کدام از این انتخاب‌ها به‌خودی‌خود بهتر نیست. مسئله این است که حجم پایین‌تنه با بالاتنه، کفش و قد لباس شما یک تصمیم آگاهانه به نظر برسد.</p>

<h2>با تیشرت باکسی کدام شلوار بهتر است؟</h2>
<p>تیشرت باکسی به دلیل عرض بیشتر و قد کنترل‌شده می‌تواند با هر سه فیت ترکیب شود. نیم‌بگ ظاهر متعادل‌تر می‌دهد، بگ حجم بیشتری وارد استایل می‌کند و فول‌بگ نتیجه جسورانه‌تری می‌سازد. اگر درباره فرم بالاتنه مطمئن نیستید، راهنمای <a href="__A1_URL__">تیشرت باکسی چیست و چه تفاوتی با اورسایز دارد</a> نقطه شروع خوبی است.</p>
<p>اگر بعد از انتخاب تیشرت باکسی بین دو سایز مردد هستید، راهنمای <a href="__A2_URL__">انتخاب سایز تیشرت باکسی مردانه</a> روش مقایسه اندازه‌ها را مرحله‌به‌مرحله توضیح می‌دهد.</p>

<h2>کفش چه اثری روی انتخاب بگ و فول‌بگ دارد؟</h2>
<p>کفش فقط یک جز جدا نیست؛ دمپای شلوار مستقیماً روی آن می‌نشیند. کتونی با حجم بیشتر معمولاً زیر دمپای باز بهتر دیده می‌شود، در حالی که کفش باریک‌تر ممکن است زیر فول‌بگ بخش زیادی از فرم خود را از دست بدهد. این قانون مطلق نیست، اما هنگام دیدن تصاویر محصول به محل برخورد دمپا و کفش توجه کنید.</p>

<h2>جنس پارچه چرا مهم است؟</h2>
<p>دو شلوار با اندازه یکسان می‌توانند به‌دلیل پارچه متفاوت، فرم متفاوتی داشته باشند. جین سفت‌تر حجم را ساختارمند نگه می‌دارد؛ پارچه نرم‌تر و لخت‌تر بیشتر ریزش می‌کند و در حرکت چین‌های نرم‌تری می‌سازد. بنابراین فقط عرض دمپا را نبینید؛ جنس و وزن پارچه هم بخشی از فیت واقعی است.</p>

<h2>اشتباه‌های رایج هنگام انتخاب فیت شلوار</h2>
<h3>فقط به اسم بگ یا فول‌بگ اعتماد می‌کنیم</h3>
<p>این نام‌ها بین برندها کاملاً استاندارد نیستند. همیشه اندازه ران، زانو، دمپا، قد و تصاویر تن‌خور را بررسی کنید.</p>

<h3>شلوار را چند سایز بزرگ‌تر می‌خریم</h3>
<p>بزرگ‌تر شدن کمر و فاق لزوماً یک بگ خوش‌فرم نمی‌سازد. اگر الگو برای فیت آزاد طراحی نشده باشد، فقط تناسب اجزای شلوار به‌هم می‌خورد.</p>

<h3>قد شلوار را نادیده می‌گیریم</h3>
<p>قد اضافه می‌تواند روی کفش چین بیشتری بسازد و ظاهر شلوار را حجیم‌تر کند. اگر این نتیجه را نمی‌خواهید، قد واقعی محصول را با شلوار مرجع خود مقایسه کنید.</p>

<h2>سؤال‌های رایج درباره بگ، نیم‌بگ و فول‌بگ</h2>
<h3>آیا فول‌بگ همیشه دمپای خیلی بزرگ دارد؟</h3>
<p>نه. فول‌بگ معمولاً حجم بیشتری دارد، اما هیچ عدد واحدی برای دمپا وجود ندارد. الگو و نسبت کل شلوار تعیین‌کننده است.</p>

<h3>برای شروع فیت آزاد، نیم‌بگ انتخاب بهتری است؟</h3>
<p>اگر هنوز به حجم زیاد عادت ندارید، نیم‌بگ معمولاً انتقال ساده‌تری از فیت‌های معمولی به استایل آزاد ایجاد می‌کند؛ اما انتخاب نهایی کاملاً سلیقه‌ای است.</p>

<h3>آیا بگ برای همه قدها مناسب است؟</h3>
<p>بله، چون «بگ» یک نسبت طراحی است نه محدودیت قد. مهم‌تر این است که قد شلوار و محل نشستن دمپا را متناسب با نتیجه‌ای که می‌خواهید انتخاب کنید.</p>

<h2>جمع‌بندی</h2>
<p>نیم‌بگ آزادی کنترل‌شده‌تر، بگ حجم واضح‌تر و فول‌بگ بیشترین حضور بصری را در پایین‌تنه ایجاد می‌کند. برای انتخاب دقیق، اسم فیت را فقط نقطه شروع بدانید و اندازه ران، زانو، دمپا، قد، فاق و جنس پارچه را با شلواری که تن‌خورش را می‌شناسید مقایسه کنید.</p>
<p><a href="__PANTS_URL__">مشاهده شلوارهای Gramiss</a>؛ برای هر مدل، مشخصات و تصاویر همان محصول را معیار نهایی تصمیم قرار دهید.</p>'''
}
ARTICLES=[A2,A3]

def call(fn,p,post=False):
 u=f'https://{host}:2083/execute/Fileman/{fn}';d=urllib.parse.urlencode(p).encode();last=None
 for attempt in range(1,5):
  try:
   r=urllib.request.Request(u if post else u+'?'+d.decode(),data=d if post else None,method='POST' if post else 'GET');r.add_header('Authorization',f'cpanel {user}:{token}')
   if post:r.add_header('Content-Type','application/x-www-form-urlencoded')
   with urllib.request.urlopen(r,context=ctx,timeout=90) as z:o=json.loads(z.read().decode('utf-8','replace'))
   q=o.get('result') if isinstance(o.get('result'),dict) else o
   if not isinstance(q,dict) or q.get('status')!=1:raise RuntimeError(str(q))
   return q.get('data')
  except Exception as exc:last=exc;print(f'Attempt {attempt}/4 {fn}: {exc}');time.sleep(attempt*2 if attempt<4 else 0)
 raise last
def read_theme(rel):
 p,n=rel.rsplit('/',1) if '/' in rel else ('',rel);d=call('get_file_content',{'dir':root if not p else root+'/'+p,'file':n,'from_charset':'_DETECT_','to_charset':'utf-8'})
 if isinstance(d,dict):
  for k in ('content','file_content','data'):
   if isinstance(d.get(k),str):return d[k]
 return d if isinstance(d,str) else ''
def save(n,c):return call('save_file_content',{'dir':'public_html','file':n,'content':c,'from_charset':'UTF-8','to_charset':'UTF-8','fallback':'0'},True)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
def get(u,follow=True):
 req=urllib.request.Request(u,headers={'User-Agent':'GramissContentWave1/1.1','Cache-Control':'no-cache','Pragma':'no-cache'});hs=[urllib.request.HTTPSHandler(context=ctx)]
 if not follow:hs.insert(0,NoRedirect())
 op=urllib.request.build_opener(*hs)
 try:
  with op.open(req,timeout=180) as z:return z.status,z.read(),z.geturl(),dict(z.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),u,dict(e.headers)
def one(t,p):
 m=re.search(p,t,re.I|re.S);return html.unescape(re.sub(r'\s+',' ',m.group(1)).strip()) if m else ''
def head(raw):
 t=raw.decode('utf-8','replace');h=t.split('</head>',1)[0];return {'title':one(h,r'<title[^>]*>(.*?)</title>'),'description':one(h,r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)'),'canonical':one(h,r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)'),'robots':one(h,r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)')}
def types(raw):
 t=raw.decode('utf-8','replace');out=[]
 for s in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',t,re.I|re.S):
  try:
   d=json.loads(s)
   def walk(x):
    if isinstance(x,dict):
     ty=x.get('@type');out.extend(ty if isinstance(ty,list) else [ty] if ty else []);[walk(v) for v in x.values()]
    elif isinstance(x,list):[walk(v) for v in x]
   walk(d)
  except:pass
 return sorted(set(str(x) for x in out))
def norm(u):return urllib.parse.unquote(u).rstrip('/')
def contains_link(text,url):return norm(url) in urllib.parse.unquote(text)

home_sha=hashlib.sha256(read_theme('front-page.php').encode()).hexdigest();print('LIVE_HOME_SHA',home_sha)
if healthy and home_sha!=healthy:raise SystemExit('ABORT Home mismatch')
data_b64=base64.b64encode(json.dumps(ARTICLES,ensure_ascii=False).encode()).decode();a1_b64=base64.b64encode(A1_SLUG.encode()).decode();nonce=hashlib.sha256((str(time.time())+home_sha).encode()).hexdigest()[:14];name='gramiss-publish-fit-cluster-'+nonce+'.php'
php=r'''<?php
header('Content-Type: application/json; charset=utf-8');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);
function d($s){return base64_decode($s);}function failj($msg,$created=[]){foreach($created as $id){if($id)wp_delete_post((int)$id,true);}http_response_code(409);echo wp_json_encode(['error'=>$msg],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);exit;}
$specs=json_decode(d('__DATA__'),true);$a1slug=sanitize_title(d('__A1__'));$cat=get_term_by('slug','fit-size-guide','category');if(!$cat||is_wp_error($cat))failj('fit-size-guide missing');
$a1=get_page_by_path($a1slug,OBJECT,'post');if(!$a1||(string)get_post_meta($a1->ID,'_gramiss_content_wave_item',true)!=='wave1-a01')failj('Article 01 prerequisite missing');
foreach($specs as $s){$slug=sanitize_title($s['slug']);$p=get_page_by_path($slug,OBJECT,'post');if($p&&(string)get_post_meta($p->ID,'_gramiss_content_wave_item',true)!==$s['marker'])failj('slug occupied: '.$s['slug']);}
$admins=get_users(['role__in'=>['administrator','editor'],'number'=>1,'orderby'=>'ID','order'=>'ASC']);$author=$admins?(int)$admins[0]->ID:1;$created=[];$ids=[];$created_flags=[];
foreach($specs as $s){$slug=sanitize_title($s['slug']);$p=get_page_by_path($slug,OBJECT,'post');if($p){$id=(int)$p->ID;$created_flags[$s['key']]=false;}else{$id=wp_insert_post(wp_slash(['post_type'=>'post','post_status'=>'publish','post_title'=>$s['title'],'post_name'=>$slug,'post_content'=>'','post_excerpt'=>$s['excerpt'],'post_author'=>$author,'post_category'=>[(int)$cat->term_id],'comment_status'=>'closed','ping_status'=>'closed']),true);if(is_wp_error($id))failj($id->get_error_message(),$created);$created[]=(int)$id;$created_flags[$s['key']]=true;update_post_meta($id,'_gramiss_content_wave_item',$s['marker']);}$ids[$s['key']]=(int)$id;}
$urls=['a01'=>get_permalink($a1->ID),'a02'=>get_permalink($ids['a02']),'a03'=>get_permalink($ids['a03'])];$pants='/shop/';$terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>false,'search'=>'شلوار','number'=>10]);if(!is_wp_error($terms)&&$terms){foreach($terms as $t){if(mb_strpos($t->name,'شلوار')!==false){$x=get_term_link($t);if(!is_wp_error($x)){$pants=$x;break;}}}}
foreach($specs as $s){$body=str_replace(['__A1_URL__','__A2_URL__','__A3_URL__','__PANTS_URL__'],[$urls['a01'],$urls['a02'],$urls['a03'],$pants],$s['body']);$id=$ids[$s['key']];$r=wp_update_post(wp_slash(['ID'=>$id,'post_status'=>'publish','post_title'=>$s['title'],'post_content'=>$body,'post_excerpt'=>$s['excerpt'],'post_category'=>[(int)$cat->term_id],'comment_status'=>'closed','ping_status'=>'closed']),true);if(is_wp_error($r))failj($r->get_error_message(),$created);update_post_meta($id,'rank_math_title',$s['seo_title']);update_post_meta($id,'rank_math_description',$s['seo_desc']);update_post_meta($id,'rank_math_focus_keyword',$s['focus']);}
$start='<!-- gramiss-wave1-related-start -->';$end='<!-- gramiss-wave1-related-end -->';$related=$start.'<section class="gramiss-related-reading"><h2>راهنماهای مرتبط</h2><ul><li><a href="'.esc_url($urls['a02']).'">راهنمای انتخاب سایز تیشرت باکسی مردانه</a></li><li><a href="'.esc_url($urls['a03']).'">تفاوت شلوار بگ، نیم‌بگ و فول‌بگ</a></li></ul></section>'.$end;$old=$a1->post_content;$new=preg_match('/'.preg_quote($start,'/').'.*?'.preg_quote($end,'/').'/s',$old)?preg_replace('/'.preg_quote($start,'/').'.*?'.preg_quote($end,'/').'/s',$related,$old):rtrim($old)."\n\n".$related;$a1changed=$new!==$old;if($a1changed){$r=wp_update_post(wp_slash(['ID'=>$a1->ID,'post_content'=>$new]),true);if(is_wp_error($r))failj($r->get_error_message(),$created);}
if(class_exists('RankMath\\Sitemap\\Cache')){\RankMath\Sitemap\Cache::invalidate_storage('post');\RankMath\Sitemap\Cache::invalidate_storage('category');}do_action('litespeed_purge_all');echo wp_json_encode(['ok'=>true,'posts'=>[['key'=>'a02','id'=>$ids['a02'],'created'=>$created_flags['a02'],'url'=>$urls['a02']],['key'=>'a03','id'=>$ids['a03'],'created'=>$created_flags['a03'],'url'=>$urls['a03']]],'a1'=>['id'=>$a1->ID,'url'=>$urls['a01'],'changed'=>$a1changed,'old'=>base64_encode($old)],'category'=>get_category_link($cat->term_id),'blog'=>get_permalink((int)get_option('page_for_posts')),'pants'=>$pants],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
'''.replace('__DATA__',data_b64).replace('__A1__',a1_b64)
save(name,php);s,b,f,h=get('https://gramiss.ir/'+name+'?t='+str(int(time.time())));print('PUBLISH_BATCH',s,b.decode('utf-8','replace'))
if s!=200:raise SystemExit('publish batch failed')
r=json.loads(b.decode('utf-8','replace'));urls={x['key']:x['url'] for x in r['posts']};a1_url=r['a1']['url'];errors=[];time.sleep(2)
# Verify all three articles and two-way cluster links
checks=[('a01',a1_url,None,None),('a02',urls['a02'],A2['seo_title'],A2['seo_desc']),('a03',urls['a03'],A3['seo_title'],A3['seo_desc'])]
texts={}
for key,u,stitle,sdesc in checks:
 s,raw,f,h=get(u+'?t='+str(int(time.time())));hi=head(raw);ty=types(raw);text=raw.decode('utf-8','replace');texts[key]=text;print('ARTICLE',key,s,f,json.dumps(hi,ensure_ascii=False),'SCHEMA',ty,'H2',len(re.findall(r'<h2\b',text,re.I)))
 if s!=200:errors.append(key+' status')
 if key!='a01':
  if stitle not in hi['title']:errors.append(key+' title')
  if hi['description']!=sdesc:errors.append(key+' description')
  if not hi['canonical'] or 'noindex' in hi['robots'].lower():errors.append(key+' index/canonical')
  if not ('BlogPosting' in ty or 'Article' in ty):errors.append(key+' schema')
  if len(re.findall(r'<h1\b',text,re.I))!=1 or len(re.findall(r'<h2\b',text,re.I))<7:errors.append(key+' headings')
if not contains_link(texts['a01'],urls['a02']) or not contains_link(texts['a01'],urls['a03']):errors.append('a01 related links')
if not contains_link(texts['a02'],a1_url) or not contains_link(texts['a02'],urls['a03']):errors.append('a02 cluster links')
if not contains_link(texts['a03'],a1_url) or not contains_link(texts['a03'],urls['a02']):errors.append('a03 cluster links')
# Blog and active category
blog=r['blog'];s,br,bf,bh=get(blog+'?t='+str(int(time.time())));bhi=head(br);bt=br.decode('utf-8','replace');print('BLOG',s,bf,json.dumps(bhi,ensure_ascii=False),'ARTICLES',len(re.findall(r'<article\b',bt,re.I)))
if s!=200 or 'noindex' in bhi['robots'].lower() or not bhi['canonical'] or A2['title'] not in bt or A3['title'] not in bt:errors.append('blog cluster')
cat=r['category'];s,cr,cf,ch=get(cat+'?t='+str(int(time.time())));chi=head(cr);ct=cr.decode('utf-8','replace');print('CATEGORY',s,cf,json.dumps(chi,ensure_ascii=False),'ARTICLES',len(re.findall(r'<article\b',ct,re.I)))
if s!=200 or 'noindex' in chi['robots'].lower() or not chi['canonical'] or A2['title'] not in ct or A3['title'] not in ct:errors.append('category cluster')
# Empty categories stay noindex
for u in ['https://gramiss.ir/category/style-guide/','https://gramiss.ir/category/buying-guide/','https://gramiss.ir/category/fabric-care/']:
 es,er,ef,eh=get(u+'?t='+str(int(time.time())));ehi=head(er);print('EMPTY_CATEGORY',u,es,ehi['robots'])
 if es!=200 or 'noindex' not in ehi['robots'].lower():errors.append('empty category '+u)
# Sitemaps
ss,sr,sf,sh=get('https://gramiss.ir/post-sitemap.xml');locs=re.findall(r'<loc>(.*?)</loc>',sr.decode('utf-8','replace'),re.I);print('SITEMAP post',ss,locs)
if ss!=200 or any(not any(norm(u)==norm(x) for x in locs) for u in [a1_url,urls['a02'],urls['a03']]):errors.append('post sitemap')
ss,sr,sf,sh=get('https://gramiss.ir/category-sitemap.xml');clocs=re.findall(r'<loc>(.*?)</loc>',sr.decode('utf-8','replace'),re.I);print('SITEMAP category',ss,clocs)
if ss!=200 or not any(norm(cat)==norm(x) for x in clocs):errors.append('category sitemap')
ps,pr,pf,ph=get('https://gramiss.ir/product-sitemap.xml');pc=len(re.findall(r'<url>',pr.decode('utf-8','replace'),re.I));print('PRODUCT_SITEMAP',ps,pc)
if ps!=200 or pc<40:errors.append('product sitemap regression')
if hashlib.sha256(read_theme('front-page.php').encode()).hexdigest()!=home_sha:errors.append('Home changed')
if errors:
 created=[x for x in r['posts'] if x.get('created')];payload=base64.b64encode(json.dumps({'created':[x['id'] for x in created],'a1_id':r['a1']['id'],'a1_changed':r['a1']['changed'],'a1_old':r['a1']['old']}).encode()).decode();rollback=r'''<?php header('Content-Type:text/plain');define('WP_USE_THEMES',false);require __DIR__.'/wp-load.php';@unlink(__FILE__);$d=json_decode(base64_decode('__PAYLOAD__'),true);foreach($d['created'] as $id){$p=get_post((int)$id);if($p&&in_array((string)get_post_meta($p->ID,'_gramiss_content_wave_item',true),['wave1-a02','wave1-a03'],true))wp_delete_post($p->ID,true);}if(!empty($d['a1_changed']))wp_update_post(wp_slash(['ID'=>(int)$d['a1_id'],'post_content'=>base64_decode($d['a1_old'])]));if(class_exists('RankMath\\Sitemap\\Cache')){\RankMath\Sitemap\Cache::invalidate_storage('post');\RankMath\Sitemap\Cache::invalidate_storage('category');}do_action('litespeed_purge_all');echo 'ROLLED_BACK';'''.replace('__PAYLOAD__',payload);rb='gramiss-rollback-fit-cluster-'+nonce+'.php';save(rb,rollback);rs,rr,rf,rh=get('https://gramiss.ir/'+rb);print('ROLLBACK',rs,rr.decode('utf-8','replace'))
 raise SystemExit('VERIFY_ERRORS '+json.dumps(errors,ensure_ascii=False))
print('PASS CONTENT WAVE 1 ARTICLES 02+03');print('A02',urls['a02']);print('A03',urls['a03']);print('PANTS_LINK',r['pants']);print('HOME SHA PRESERVED',home_sha)
